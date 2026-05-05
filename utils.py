from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
import locale
import random
import pytz
import os

# Configurar idioma para fechas (Intenta cargar español, si falla usa el sistema)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'spanish')
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

def enmascarar_nombre(nombre: str) -> str:
    if not nombre: return ""
    partes = str(nombre).split()
    return " ".join([p[:3] + "***" if len(p) > 3 else p + "***" for p in partes])

def formatear_telefono_co(numero: str) -> str:
    if not numero: return ""
    digitos = "".join(ch for ch in str(numero) if ch.isdigit())
    if len(digitos) == 10:
        return f"{digitos[:3]} {digitos[3:6]} {digitos[6:]}"
    return str(numero)

def limpiar_y_formatear_valor(valor_raw):
    """Limpia el input y devuelve formato $ 10.000,00"""
    try:
        # Convertir a string y limpiar caracteres comunes si vienen del form
        val_str = str(valor_raw).replace("$", "").replace(" ", "").replace(".", "").replace(",", "")
        valor_float = float(val_str)
        # Formateo con separador de miles '.' y decimales ','
        fmt = "{:,.2f}".format(valor_float).replace(",", "X").replace(".", ",").replace("X", ".")
        return f"$ {fmt}"
    except:
        return "$ 0,00"

# --- FUNCIONES DE GENERACIÓN ---

def generar_comprobante(data, config):
    template_path = config.get("template")
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config.get("styles", {})
    font_path = config.get("font")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"No se encontró el template: {template_path}")

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Lógica de fecha
    try:
        tz = pytz.timezone("America/Bogota")
        now = datetime.now(tz)
        fecha_default = now.strftime("%d de %B de %Y a las %I:%M %p").lower()
    except:
        fecha_default = datetime.now().strftime("%d/%m/%Y %H:%M")

    datos = {
        "nombre": data.get("nombre", ""),
        "telefono": formatear_telefono_co(data.get("telefono", "")),
        "valor1": limpiar_y_formatear_valor(data.get("valor", 0)),
        "fecha": data.get("fecha_manual") or fecha_default,
        "referencia": data.get("referencia_manual") or f"M{random.randint(1000000, 9999999)}"
    }

    # Dibujar campos según el diccionario de estilos
    for campo, texto in datos.items():
        if campo in styles:
            s = styles[campo]
            font = cargar_fuente(font_path, s["size"])
            draw.text(s["pos"], str(texto), font=font, fill=s["color"])

    image.save(output_path)
    return output_path

# --- WRAPPERS ---
def generar_comprobante_nuevo(data, config):
    return generar_comprobante(data, config)

def generar_comprobante_anulado(data, config):
    return generar_comprobante(data, config)

def generar_comprobante_ahorros(data, config):
    """Generación genérica basada estrictamente en lo que venga en 'styles'"""
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]
    
    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    for campo, style in styles.items():
        # Si el campo existe en data, se dibuja
        if campo in data:
            texto = str(data.get(campo, ""))
            font = cargar_fuente(font_path, style["size"])
            draw.text(style["pos"], texto, font=font, fill=style["color"])
    
    image.save(output_path)
    return output_path

# Alias para mantener compatibilidad
generar_comprobante_daviplata = generar_comprobante_ahorros
generar_comprobante_bc_nq_t = generar_comprobante_ahorros
generar_comprobante_bc_qr = generar_comprobante_ahorros
generar_comprobante_nequi_bc = generar_comprobante
generar_comprobante_nequi_ahorros = generar_comprobante

def generar_movimiento_bancolombia(data, config):
    template_path = config["template"]
    output_path = f"mov_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Procesar valor negativo para movimientos
    try:
        val_str = str(data.get("valor", 0)).replace("$", "").replace(".", "").replace(",", "")
        valor_raw = abs(float(val_str))
        valor_fmt = f"-$ {valor_raw:,.0f}".replace(",", ".") + ",00"
    except:
        valor_fmt = "-$ 0,00"

    if "nombre" in styles:
        s = styles["nombre"]
        font_n = cargar_fuente(font_path, s["size"])
        draw.text(s["pos"], str(data.get("nombre", "")).upper(), font=font_n, fill=s["color"])

    if "valor" in styles:
        s = styles["valor"]
        font_v = cargar_fuente(font_path, s.get("size", 22))
        draw.text(s.get("pos", (400, 715)), valor_fmt, font=font_v, fill=s["color"])

    image.save(output_path)
    return output_path
