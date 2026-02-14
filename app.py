from flask import Flask, render_template

app = Flask(__name__)

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Página carta
@app.route("/carta")
def carta():
    return render_template("carta.html")

# Página canción (opcional)
@app.route("/cancion")
def cancion():
    return render_template("cancion.html")

if __name__ == "__main__":
    app.run

