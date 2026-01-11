from flask import request
from werkzeug.utils import secure_filename
from flask import Flask, render_template
from flask_socketio import SocketIO
import os, time

app = Flask(__name__)
socketio = SocketIO(app)

UPLOADS = "uploads"
HISTORY = "history.txt"
os.makedirs(UPLOADS, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def enviar_historico():
    if os.path.exists(HISTORY):
        with open(HISTORY, "r", encoding="utf-8") as f:
            for linha in f:
                socketio.send(linha.strip())

@socketio.on("message")
def mensagem(msg):
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    socketio.send(msg)

def limpar_arquivos():
    agora = time.time()
    for arq in os.listdir(UPLOADS):
        caminho = os.path.join(UPLOADS, arq)
        if os.path.isfile(caminho):
            if (agora - os.path.getctime(caminho)) > 7 * 86400:
                os.remove(caminho)

limpar_arquivos()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return "Nenhum arquivo", 400

    nome = secure_filename(file.filename)
    caminho = os.path.join(UPLOADS, nome)
    file.save(caminho)

    socketio.send(f"📁 Arquivo enviado: {nome}")
    return "OK", 200

