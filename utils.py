from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
import locale
import random
import pytz
import os

# Configurar idioma español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

def draw_text_with_outline(draw, position, text, font, fill, outline_fill="#2e2b33", outline_width=2):
    # Dibujamos el texto. El outline es opcional dependiendo del diseño
    draw.text(position, str(text), font=font, fill=fill)

def enmascarar_nombre(nombre: str) -> str:
    if not nombre: return ""
    partes = nombre.split()
    partes_mask = []
    for palabra in partes:
        if len(palabra) <= 3:
            partes_mask.append(palabra + "***")
        else:
            partes_mask.append(palabra[:3] + "***")
    return " ".join(partes_mask)

def cargar_fuente(font_path, size):
    try:
        # Intentar cargar la fuente desde la ruta
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        else:
            # Si no existe, usar la fuente por defecto de PIL
            return ImageFont.load_default()
    except:
        return ImageFont.load_default()

# --- FUNCIÓN PRINCIPAL NEQUI ---
def generar_comprobante(data, config=None):
    # Si no hay config, usamos una base por defecto para evitar errores
    template_path = config.get("template", "nequi_template.png") if config else "nequi_template.png"
    font_path = config.get("font", "font.ttf") if config else "font.ttf"
    styles = config.get("styles", {}) if config else {}
    
    output_path = f"gen_{uuid.uuid4().hex}.png"
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"No se encontró el template: {template_path}")

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Preparar Datos
    now = datetime.now(pytz.timezone("America/Bogota"))
    fecha_auto = now.strftime("%d de %m de %Y a las %I:%M %p").lower()
    
    valor_raw = float(str(data.get("valor", 0)).replace(".", "").replace(",", ""))
    valor_fmt = "$ {:,.2f}".format(valor_raw).replace(",", "X").replace(".", ",").replace("X", ".")

    datos = {
        "nombre": data.get("nombre", ""),
        "telefono": data.get("telefono", ""),
        "valor1": valor_fmt,
        "fecha": data.get("fecha_manual", fecha_auto),
        "referencia": data.get("referencia_manual", f"M{random.randint(1000000, 9999999)}")
    }

    # Dibujar
    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            font = cargar_fuente(font_path, style.get("size", 25))
            draw.text(style["pos"], str(texto), font=font, fill=style.get("color", "#2e2b33"))

    image.save(output_path)
    return output_path

# --- FUNCIÓN MOVIMIENTO BANCOLOMBIA ---
def generar_movimiento_bancolombia(data, config=None):
    template_path = config.get("template", "bancolombia_mov.png") if config else "bancolombia_mov.png"
    font_path = config.get("font", "font.ttf") if config else "font.ttf"
    styles = config.get("styles", {}) if config else {}
    
    output_path = f"mov_{uuid.uuid4().hex}.png"

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"No se encontró el template de movimiento: {template_path}")

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Lógica de dibujo de montos (Simplificada para estabilidad)
    valor_raw = abs(float(str(data.get("valor", 0)).replace(".", "").replace(",", "")))
    valor_fmt = f"{valor_raw:,.0f}".replace(",", ".") + ",00"
    
    # Dibujar Nombre en Mayúsculas
    if "nombre" in styles:
        s = styles["nombre"]
        font_n = cargar_fuente(font_path, s.get("size", 20))
        draw.text(s["pos"], data.get("nombre", "").upper(), font=font_n, fill=s.get("color", "black"))

    # Dibujar Valor
    if "valor" in styles:
        s = styles["valor"]
        font_v = cargar_fuente(font_path, s.get("size", 22))
        # Posicionamiento simple para evitar errores de medición
        draw.text(s.get("pos", (400, 715)), f"-$ {valor_fmt}", font=font_v, fill=s.get("color", "#333333"))

    image.save(output_path)
    return output_path

# Las demás funciones (Daviplata, Ahorros, etc.) deben seguir este mismo patrón de cargar_fuente
