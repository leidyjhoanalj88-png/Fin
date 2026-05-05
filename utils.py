from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
import locale
import random
import pytz
import os

# Configurar idioma
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

# --- HELPERS DE CARGA Y SEGURIDAD ---
def cargar_fuente(font_path, size):
    try:
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def draw_text_with_outline(draw, position, text, font, fill, outline_fill="#2e2b33", outline_width=2):
    draw.text(position, str(text), font=font, fill=fill)

def enmascarar_nombre(nombre: str) -> str:
    if not nombre: return ""
    partes = nombre.split()
    return " ".join([p[:3] + "***" if len(p) > 3 else p + "***" for p in partes])

def formatear_telefono_co(numero: str) -> str:
    digitos = "".join(ch for ch in numero if ch.isdigit())
    if len(digitos) == 10:
        return f"{digitos[:3]} {digitos[3:6]} {digitos[6:]}"
    return numero

# --- FUNCIONES DE GENERACIÓN ---

def generar_comprobante(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Lógica de fecha y valor
    now = datetime.now(pytz.timezone("America/Bogota"))
    fecha = data.get("fecha_manual") or now.strftime("%d de %m de %Y a las %I:%M %p").lower()
    valor_fmt = "$ {:,.2f}".format(float(str(data.get("valor", 0)).replace(".",""))).replace(",", "X").replace(".", ",").replace("X", ".")
    
    datos = {
        "nombre": data.get("nombre", ""),
        "telefono": formatear_telefono_co(data.get("telefono", "")),
        "valor1": valor_fmt,
        "fecha": fecha,
        "referencia": data.get("referencia_manual") or f"M{random.randint(1000000, 9999999)}"
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            font = cargar_fuente(font_path, style["size"])
            draw.text(style["pos"], str(texto), font=font, fill=style["color"])

    image.save(output_path)
    return output_path

def generar_comprobante_nuevo(data, config):
    # Esta es la que causaba el error de importación
    return generar_comprobante(data, config)

def generar_comprobante_anulado(data, config):
    return generar_comprobante(data, config)

def generar_comprobante_ahorros(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]
    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    for campo, style in styles.items():
        texto = str(data.get(campo, ""))
        font = cargar_fuente(font_path, style["size"])
        draw.text(style["pos"], texto, font=font, fill=style["color"])
    
    image.save(output_path)
    return output_path

def generar_comprobante_daviplata(data, config):
    return generar_comprobante_ahorros(data, config)

def generar_comprobante_bc_nq_t(data, config):
    return generar_comprobante_ahorros(data, config)

def generar_comprobante_bc_qr(data, config):
    return generar_comprobante_ahorros(data, config)

def generar_comprobante_nequi_bc(data, config):
    return generar_comprobante(data, config)

def generar_comprobante_nequi_ahorros(data, config):
    return generar_comprobante(data, config)

def generar_movimiento_bancolombia(data, config):
    template_path = config["template"]
    output_path = f"mov_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    valor_raw = abs(float(str(data.get("valor", 0)).replace(".","")))
    valor_fmt = f"-$ {valor_raw:,.0f}".replace(",", ".") + ",00"

    if "nombre" in styles:
        s = styles["nombre"]
        font_n = cargar_fuente(font_path, s["size"])
        draw.text(s["pos"], data.get("nombre", "").upper(), font=font_n, fill=s["color"])

    if "valor" in styles:
        s = styles["valor"]
        font_v = cargar_fuente(font_path, s.get("size", 22))
        draw.text(s.get("pos", (400, 715)), valor_fmt, font=font_v, fill=s["color"])

    image.save(output_path)
    return output_path
