"""
Generador de imágenes para los tips de finanzas personales.
Crea una tarjeta cuadrada (1080x1080, tamaño ideal para Facebook/Instagram)
con el texto del tip centrado sobre un fondo degradado, y el nombre
de la página al pie, similar al estilo de tarjetas de cita motivacional.
"""

import random
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

import os

WIDTH, HEIGHT = 1080, 1080

# Rutas relativas a este archivo, para que funcione sin importar el
# sistema de archivos del servidor (Railway no siempre trae fuentes instaladas)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = os.path.join(_BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")
FONT_REGULAR = os.path.join(_BASE_DIR, "fonts", "DejaVuSans.ttf")

PAGE_NAME = "Ponche Finanzas"

# Paletas de degradado (de arriba a abajo) - tonos oscuros y elegantes,
# rotan para que no todas las tarjetas se vean iguales.
GRADIENTS = [
    ((10, 20, 40), (25, 45, 90)),      # azul noche
    ((15, 35, 25), (30, 70, 45)),      # verde bosque
    ((35, 15, 40), (70, 30, 80)),      # morado
    ((20, 20, 20), (55, 45, 15)),      # dorado oscuro
    ((10, 30, 35), (20, 60, 65)),      # verde azulado
]


def _draw_gradient(draw, color_top, color_bottom):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _wrap_text(text, font, max_width, draw):
    """Ajusta el texto a varias líneas según el ancho máximo permitido."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        prueba = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), prueba, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = prueba
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# Rango de caracteres emoji comunes, para quitarlos del texto de la imagen
# (la fuente no los renderiza y deja cuadros vacíos)
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]+",
    flags=re.UNICODE,
)


def _quitar_emojis(texto: str) -> str:
    return _EMOJI_PATTERN.sub("", texto).strip()


def generar_imagen_tip(texto_tip: str, output_path: str = "tip_card.png") -> str:
    """
    Genera una imagen tipo tarjeta con el tip centrado y la guarda en output_path.
    Devuelve la ruta del archivo generado.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    color_top, color_bottom = random.choice(GRADIENTS)
    _draw_gradient(draw, color_top, color_bottom)

    # Quitamos el emoji para la imagen (la fuente no lo soporta);
    # el emoji se conserva en el texto que acompaña la publicación
    texto = _quitar_emojis(texto_tip)

    font_size = 62
    font = ImageFont.truetype(FONT_BOLD, font_size)
    max_text_width = WIDTH - 160  # márgenes laterales

    lines = _wrap_text(texto, font, max_text_width, draw)

    # Si el texto es muy largo (muchas líneas), reduce el tamaño de fuente
    while len(lines) > 7 and font_size > 36:
        font_size -= 4
        font = ImageFont.truetype(FONT_BOLD, font_size)
        lines = _wrap_text(texto, font, max_text_width, draw)

    line_height = font.getbbox("Ay")[3] + 22
    total_text_height = line_height * len(lines)
    start_y = (HEIGHT - total_text_height) // 2 - 40

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (WIDTH - line_width) // 2
        y = start_y + i * line_height
        # Sombra sutil para legibilidad
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 120))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))

    # Marca de la página al pie
    footer_font = ImageFont.truetype(FONT_REGULAR, 34)
    footer_text = PAGE_NAME
    bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_width = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - footer_width) // 2, HEIGHT - 90),
        footer_text,
        font=footer_font,
        fill=(220, 220, 220),
    )

    img.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    # Prueba rápida
    ruta = generar_imagen_tip(
        "💰 Antes de gastar, decide cuánto vas a ahorrar. El ahorro no es lo que sobra, es lo primero que apartas."
    )
    print(f"Imagen generada en: {ruta}")
