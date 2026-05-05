from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
import locale
import random
import pytz
import os

# Configuración de idioma
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'spanish')
    except:
        pass

def cargar_fuente(font_path, size):
    try:
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        print(f"⚠️ Advertencia: No se encontró la fuente en {font_path}. Usando default.")
        return ImageFont.load_default()
    except Exception as e:
        return ImageFont.load_default()

def limpiar_y_formatear_valor(valor_raw):
    try:
        val_str = str(valor_raw).replace("$", "").replace(" ", "").replace(".", "").replace(",", "")
        valor_float = float(val_str)
        fmt = "{:,.2f}".format(valor_float).replace(",", "X").replace(".", ",").replace("X", ".")
        return f"$ {fmt}"
    except:
        return "$ 0,00"

def generar_comprobante(data, config):
    template_path = config.get("template")
    # Verificación crítica de existencia de imagen
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"❌ Error: El archivo de imagen '{template_path}' no existe en la carpeta img.")

    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config.get("styles", {})
    font_path = config.get("font")

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
        "telefono": data.get("telefono", ""),
        "valor1": limpiar_y_formatear_valor(data.get("valor", 0)),
        "fecha": data.get("fecha_manual") or fecha_default,
        "referencia": data.get("referencia_manual") or f"M{random.randint(1000000, 9999999)}"
    }

    for campo, texto in datos.items():
        if campo in styles:
            s = styles[campo]
            # Usar la fuente del campo si existe, si no la general del config
            f_path = s.get("font", font_path)
            font = cargar_fuente(f_path, s["size"])
            draw.text(s["pos"], str(texto), font=font, fill=s["color"])

    image.save(output_path)
    return output_path

# Wrappers para compatibilidad
def generar_comprobante_nequi_bc(data, config):
    return generar_comprobante(data, config)

def generar_comprobante_nuevo(data, config):
    return generar_comprobante(data, config)
