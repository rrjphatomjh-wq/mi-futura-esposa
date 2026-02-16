from flask import Flask, render_template

app = Flask(__name__)

# Página principal
@app.route("/")
def index():
    return render_template("index.html")
from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)

# Crear base de datos si no existe
def init_db():
    conn = sqlite3.connect("visitas.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            pais TEXT,
            ciudad TEXT,
            user_agent TEXT,
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Ruta principal
@app.route("/")
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # Obtener geolocalización
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}").json()
        pais = geo.get("country", "Desconocido")
        ciudad = geo.get("city", "Desconocido")
    except:
        pais = "Error"
        ciudad = "Error"

    user_agent = request.headers.get("User-Agent")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar en base de datos
    conn = sqlite3.connect("visitas.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO visitas (ip, pais, ciudad, user_agent, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (ip, pais, ciudad, user_agent, fecha))
    conn.commit()
    conn.close()

    return render_template("index.html")


@app.route("/carta")
def carta():
    return render_template("carta.html")


@app.route("/cancion")
def cancion():
    return render_template("cancion.html")


# PANEL SECRETO
@app.route("/admin")
def admin():
    conn = sqlite3.connect("visitas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM visitas ORDER BY id DESC")
    datos = c.fetchall()
    conn.close()

    return render_template("admin.html", visitas=datos)


if __name__ == "__main__":
    app.run(debug=True)
