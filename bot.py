"""
Bot de Facebook - Tips de Finanzas Personales
Publica automáticamente un tip diario en la página de Facebook "Ponche Finanzas".

Variables de entorno necesarias (configúralas en Railway, NUNCA en el código):
    FB_PAGE_ID       -> ID de tu página de Facebook (Ponche Finanzas)
    FB_ACCESS_TOKEN  -> Token de acceso del Usuario del Sistema (no caduca)
    POST_HOUR        -> Hora del día para publicar (24h, ej: 9 para las 9:00 AM). Opcional, default 9.

El bot corre en un loop: cada minuto revisa si ya es la hora de publicar,
y si es así, elige el siguiente tip del banco (rotación secuencial diaria)
y lo publica en la página.
"""

import os
import time
import json
import logging
from datetime import datetime

import requests

from tips import TIPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bot_facebook_finanzas")

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
POST_HOUR = int(os.environ.get("POST_HOUR", "9"))
GRAPH_API_VERSION = "v21.0"
STATE_FILE = "state.json"


def cargar_estado():
    """Lee el índice del último tip publicado y la última fecha de publicación."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"ultimo_indice": -1, "ultima_fecha": ""}


def guardar_estado(estado):
    with open(STATE_FILE, "w") as f:
        json.dump(estado, f)


def publicar_en_facebook(mensaje: str):
    """Publica un mensaje de texto en la página de Facebook usando la Graph API."""
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        log.error("Faltan las variables de entorno FB_PAGE_ID o FB_ACCESS_TOKEN.")
        return False

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{FB_PAGE_ID}/feed"
    payload = {
        "message": mensaje,
        "access_token": FB_ACCESS_TOKEN,
    }

    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        log.info(f"Publicado correctamente. ID del post: {data.get('id')}")
        return True
    except requests.exceptions.RequestException as e:
        log.error(f"Error al publicar en Facebook: {e}")
        if hasattr(e, "response") and e.response is not None:
            log.error(f"Respuesta de Facebook: {e.response.text}")
        return False


def obtener_siguiente_tip(estado):
    """Rota secuencialmente por la lista de tips."""
    siguiente_indice = (estado["ultimo_indice"] + 1) % len(TIPS)
    return siguiente_indice, TIPS[siguiente_indice]


def ya_publico_hoy(estado):
    hoy = datetime.now().strftime("%Y-%m-%d")
    return estado.get("ultima_fecha") == hoy


def ciclo_principal():
    log.info("Bot de Facebook - Tips de Finanzas Personales iniciado.")
    log.info(f"Hora programada de publicación: {POST_HOUR}:00")

    while True:
        ahora = datetime.now()
        estado = cargar_estado()

        if ahora.hour == POST_HOUR and not ya_publico_hoy(estado):
            indice, tip = obtener_siguiente_tip(estado)
            log.info(f"Publicando tip #{indice + 1}: {tip[:50]}...")

            exito = publicar_en_facebook(tip)
            if exito:
                estado["ultimo_indice"] = indice
                estado["ultima_fecha"] = ahora.strftime("%Y-%m-%d")
                guardar_estado(estado)

        # Revisa cada 60 segundos
        time.sleep(60)


if __name__ == "__main__":
    ciclo_principal()
