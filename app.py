from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os, time, json

app = Flask(__name__)
app.config["SECRET_KEY"] = "segredo-super-privado"
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOADS = "uploads"
HISTORY = "history.json"

os.makedirs(UPLOADS, exist_ok=True)

# ------------------------
# HISTÓRICO
# ------------------------
def carregar_historico():
    if os.path.exists(HISTORY):
        with open(HISTORY, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_historico(dados):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False)

# ------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:nome>")
def arquivos(nome):
    return send_from_directory(UPLOADS, nome)

# ------------------------
@socketio.on("connect")
def conectar():
    for msg in carregar_historico():
        socketio.send(msg)

@socketio.on("message")
def mensagem(data):
    historico = carregar_historico()
    historico.append(data)
    salvar_historico(historico)
    socketio.send(data)

# ------------------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    nick = request.form.get("nick", "Anon")

    if not file:
        return "Erro", 400

    nome = secure_filename(file.filename)
    caminho = os.path.join(UPLOADS, nome)
    file.save(caminho)

    ext = nome.split(".")[-1].lower()

    tipo = "arquivo"
    if ext in ["png", "jpg", "jpeg", "gif", "webp"]:
        tipo = "imagem"
    elif ext in ["mp3", "wav", "ogg"]:
        tipo = "audio"

    msg = {
        "nick": nick,
        "tipo": tipo,
        "nome": nome,
        "url": f"/uploads/{nome}"
    }

    historico = carregar_historico()
    historico.append(msg)
    salvar_historico(historico)

    socketio.send(msg)
    return "OK"

# ------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
