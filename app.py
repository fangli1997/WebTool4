
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import random
import secrets
import string
import json

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>RandomBox</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}
body{
    margin:0;background:#10111c;color:white;
    font-family:Arial,sans-serif;padding:30px 15px;
}
.container{max-width:650px;margin:auto}
h1{text-align:center;color:#a78bfa;font-size:38px}
.subtitle{text-align:center;color:#aaa}
.card{
    background:#1c1d2d;padding:22px;margin:18px 0;
    border-radius:15px;border:1px solid #303149;
}
h2{font-size:19px;color:#c4b5fd}
input,textarea,button{
    width:100%;padding:13px;margin-top:10px;
    border-radius:8px;border:0;font-size:15px;
}
input,textarea{background:#303149;color:white}
button{
    background:#8b5cf6;color:white;
    cursor:pointer;font-weight:bold;
}
button:hover{background:#7c3aed}
.result{
    background:#11121e;padding:15px;margin-top:12px;
    border-radius:8px;text-align:center;
    font-size:22px;overflow-wrap:anywhere;
}
.small{font-size:12px;color:#888;text-align:center}
</style>
</head>
<body>
<div class="container">
<h1>🎲 RandomBox</h1>
<p class="subtitle">Your all-in-one random generator</p>

<div class="card">
<h2>🔢 Random Number</h2>
<input id="min" type="number" value="1" placeholder="Minimum">
<input id="max" type="number" value="100" placeholder="Maximum">
<button onclick="run('number')">Generate Number</button>
<div class="result" id="numberResult">---</div>
</div>

<div class="card">
<h2>🎯 Random Picker</h2>
<textarea id="items" placeholder="Enter items separated by commas"></textarea>
<button onclick="run('choice')">Pick Random Item</button>
<div class="result" id="choiceResult">---</div>
</div>

<div class="card">
<h2>🪙 Coin Flip</h2>
<button onclick="run('coin')">Flip Coin</button>
<div class="result" id="coinResult">---</div>
</div>

<div class="card">
<h2>🎲 Dice Roller</h2>
<button onclick="run('dice')">Roll Dice</button>
<div class="result" id="diceResult">---</div>
</div>

<div class="card">
<h2>🔐 Password Generator</h2>
<input id="length" type="number" value="16" min="4" max="128">
<button onclick="run('password')">Generate Password</button>
<div class="result" id="passwordResult">---</div>
</div>

<p class="small">RandomBox • Built with Python</p>
</div>

<script>
async function run(action){
    let data = {action};

    if(action === 'number'){
        data.min = document.getElementById('min').value;
        data.max = document.getElementById('max').value;
    }
    if(action === 'choice'){
        data.items = document.getElementById('items').value;
    }
    if(action === 'password'){
        data.length = document.getElementById('length').value;
    }

    try{
        const response = await fetch('/generate',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify(data)
        });
        const result = await response.json();
        document.getElementById(action+'Result').textContent =
            result.result ?? result.error;
    }catch(e){
        alert('Something went wrong!');
    }
}
</script>
</body>
</html>
"""


class RandomBox(BaseHTTPRequestHandler):

    def send_response_data(self, data, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "null")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.send_response_data(
                HTML.encode(), "text/html; charset=utf-8"
            )
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/generate":
            self.send_error(404)
            return

        try:
            size = int(self.headers.get("Content-Length", 0))
            if size > 10000:
                raise ValueError("Request too large")

            data = json.loads(self.rfile.read(size))
            action = data.get("action")

            if action == "number":
                low = int(data["min"])
                high = int(data["max"])
                if low > high:
                    raise ValueError("Minimum cannot exceed maximum")
                if high - low > 10**12:
                    raise ValueError("Range is too large")
                result = random.randint(low, high)

            elif action == "choice":
                items = [
                    x.strip() for x in data["items"].split(",")
                    if x.strip()
                ]
                if not items:
                    raise ValueError("Enter at least one item")
                result = random.choice(items)

            elif action == "coin":
                result = random.choice(["Heads 🪙", "Tails 🪙"])

            elif action == "dice":
                result = random.randint(1, 6)

            elif action == "password":
                length = int(data["length"])
                if not 4 <= length <= 128:
                    raise ValueError("Length must be 4–128")
                chars = string.ascii_letters + string.digits + "!@#$%"
                result = ''.join(
                    secrets.choice(chars) for _ in range(length)
                )

            else:
                raise ValueError("Unknown action")

            output = {"result": result}

        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            output = {"error": str(e)}

        self.send_response_data(
            json.dumps(output).encode(),
            "application/json"
        )


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), RandomBox)
    print("RandomBox running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
        server.server_close()
