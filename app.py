from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "segredo"
socketio = SocketIO(app)

UPLOADS = "uploads"
HISTORY = "history.txt"

os.makedirs(UPLOADS, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:nome>")
def arquivos(nome):
    return send_from_directory(UPLOADS, nome)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return "Sem arquivo", 400

    nome = secure_filename(file.filename)
    caminho = os.path.join(UPLOADS, nome)
    file.save(caminho)

    return {
        "tipo": "arquivo",
        "nome": nome,
        "url": f"/uploads/{nome}"
    }

@socketio.on("connect")
def enviar_historico():
    if os.path.exists(HISTORY):
        with open(HISTORY, "r", encoding="utf-8") as f:
            for linha in f:
                socketio.send(linha.strip())

@socketio.on("message")
def receber(msg):
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

    socketio.send(msg)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
