from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime
import os

app = Flask(__name__)

# ==============================
# CONFIGURACIÓN TELEGRAM
# ==============================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def enviar_telegram(mensaje):
    if TELEGRAM_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": mensaje
        }
        try:
            requests.post(url, data=data)
        except:
            pass


# ==============================
# BASE DE DATOS
# ==============================

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


# ==============================
# RUTA PRINCIPAL
# ==============================

@app.route("/")
def home():
    # Obtener IP real en Render
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # Geolocalización
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
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

    # Mensaje para Telegram
    mensaje = f"""
🚨 NUEVA VISITA 🚨

🌍 IP: {ip}
🌎 País: {pais}
🏙 Ciudad: {ciudad}
🕒 Fecha: {fecha}
📱 Dispositivo: {user_agent}
"""

    enviar_telegram(mensaje)

    return render_template("index.html")


# ==============================
# OTRAS RUTAS
# ==============================

@app.route("/carta")
def carta():
    return render_template("carta.html")


@app.route("/cancion")
def cancion():
    return render_template("cancion.html")


# ==============================
# PANEL ADMIN
# ==============================

@app.route("/admin")
def admin():
    conn = sqlite3.connect("visitas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM visitas ORDER BY id DESC")
    datos = c.fetchall()
    conn.close()

    return render_template("admin.html", visitas=datos)


# ==============================
# INICIO
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
