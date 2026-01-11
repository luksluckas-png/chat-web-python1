from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os, time

app = Flask(__name__)
socketio = SocketIO(app)

UPLOADS = "uploads"
HISTORY = "history.txt"

os.makedirs(UPLOADS, exist_ok=True)

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Servir arquivos enviados
@app.route("/uploads/<filename>")
def baixar_arquivo(filename):
    return send_from_directory(UPLOADS, filename)

# Histórico ao conectar
@socketio.on("connect")
def enviar_historico():
    if os.path.exists(HISTORY):
        with open(HISTORY, "r", encoding="utf-8") as f:
            for linha in f:
                socketio.send(linha.strip())

# Mensagens de texto
@socketio.on("message")
def mensagem(msg):
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    socketio.send(msg)

# Upload de arquivos
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return "Nenhum arquivo", 400

    nome = secure_filename(file.filename)
    caminho = os.path.join(UPLOADS, nome)
    file.save(caminho)

    url = f"/uploads/{nome}"

    socketio.send({
        "tipo": "arquivo",
        "nome": nome,
        "url": url
    })

    return "OK", 200

# Limpar arquivos antigos (7 dias)
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
