from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
import locale
import random
import pytz
import time
import os

# Configurar idioma español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Colombia.1252')
    except:
        pass


def draw_text_with_outline(draw, position, text, font, fill, outline_fill, outline_width):
    x, y = position
    draw.text((x, y), text, font=font, fill=fill)


def dibujar_valor_movimiento(draw, base_style, valor, font_path, ancho_imagen, decimal_style=None):
    valor = valor if valor is not None else 0
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        valor = 0.0

    valor_formateado = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    valor_str = f"-$ {valor_formateado}" if valor < 0 else f"$ {valor_formateado}"
    entero, decimal = valor_str[:-3], valor_str[-3:]

    pos_y = base_style["pos"][1]
    limite_izquierdo = 100
    limite_derecho = 580
    margen_derecho = 20

    size_entero = base_style["size"]
    size_decimal = int(size_entero * 0.75)

    font_entero = ImageFont.truetype(base_style.get("font", font_path), size_entero)
    font_decimal = ImageFont.truetype(decimal_style.get("font", font_path) if decimal_style else font_path, size_decimal)

    ancho_entero = draw.textlength(entero, font=font_entero)
    ancho_decimal = draw.textlength(decimal, font=font_decimal)

    while (ancho_entero + ancho_decimal) > (limite_derecho - limite_izquierdo - margen_derecho) and size_entero > 8:
        size_entero -= 1
        size_decimal = int(size_entero * 0.75)
        font_entero = ImageFont.truetype(base_style.get("font", font_path), size_entero)
        font_decimal = ImageFont.truetype(decimal_style.get("font", font_path) if decimal_style else font_path, size_decimal)
        ancho_entero = draw.textlength(entero, font=font_entero)
        ancho_decimal = draw.textlength(decimal, font=font_decimal)

    x_decimal = limite_derecho - margen_derecho
    x_entero = x_decimal - ancho_entero

    if x_entero < limite_izquierdo:
        x_entero = limite_izquierdo
        x_decimal = x_entero + ancho_entero

    x_entero -= 13
    x_decimal -= 13

    bbox_entero = font_entero.getbbox("0")
    bbox_decimal = font_decimal.getbbox("0")
    offset_y = bbox_entero[3] - bbox_decimal[3]
    decimal_y = pos_y + offset_y

    draw_text_with_outline(draw, (x_entero, pos_y), entero, font_entero, base_style["color"], "white", 2)
    draw.text((x_decimal, decimal_y), decimal, font=font_decimal,
              fill=decimal_style.get("color", base_style["color"]) if decimal_style else base_style["color"])


# ===== Helper: formatear teléfono =====
def formatear_telefono_co(numero: str) -> str:
    if not numero:
        return ""
    digitos = "".join(ch for ch in numero if ch.isdigit())
    if digitos.startswith("57") and len(digitos) == 12:
        digitos = digitos[2:]
    if len(digitos) == 10:
        return f"{digitos[:3]} {digitos[3:6]} {digitos[6:]}"
    return numero


# ===== Helper: enmascarar nombre =====
def enmascarar_nombre(nombre: str) -> str:
    if not nombre:
        return ""
    partes = nombre.split()
    partes_mask = []
    for palabra in partes:
        if len(palabra) <= 3:
            partes_mask.append(palabra + "***")
        else:
            visibles = palabra[:3]
            partes_mask.append(visibles + "***")
    return " ".join(partes_mask)


# ===== Helper: safe float =====
def _safe_float(valor, default=0.0):
    try:
        return float(valor) if valor is not None else default
    except (TypeError, ValueError):
        return default


# ===== Helper: safe int =====
def _safe_int(valor, default=0):
    try:
        return int(valor) if valor is not None else default
    except (TypeError, ValueError):
        return default


def generar_comprobante(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    tipo_movimiento = "valor1" in styles and "nombre" in styles and "valor_decimal" in styles
    es_comprobante_qr = config["output"] == "comprobante_qr_generado.png"
    es_comprobante4 = config["output"] == "comprobante4_generado.png"

    if tipo_movimiento:
        decimal_style = styles.get("valor_decimal")
        # ✅ Parche: valor seguro
        valor_seguro = _safe_float(data.get("valor"), 0.0)
        dibujar_valor_movimiento(draw, styles["valor1"], valor_seguro, font_path, image.width, decimal_style)
        font_nombre = ImageFont.truetype(styles["nombre"].get("font", font_path), styles["nombre"]["size"])
        draw_text_with_outline(draw, styles["nombre"]["pos"], str(data.get("nombre", "")), font_nombre, styles["nombre"]["color"], "white", 2)
    else:
        # Fecha
        if "fecha_manual" in data and data["fecha_manual"]:
            fecha = data["fecha_manual"]
        else:
            meses_es = {
                "january": "enero", "february": "febrero", "march": "marzo", "april": "abril",
                "may": "mayo", "june": "junio", "july": "julio", "august": "agosto",
                "september": "septiembre", "october": "octubre", "november": "noviembre", "december": "diciembre"
            }
            now = datetime.now(pytz.timezone("America/Bogota"))
            mes_en = now.strftime("%B").lower()
            mes = meses_es.get(mes_en, mes_en)
            fecha = now.strftime(f"%d de {mes} de %Y a las %I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")

        # Referencia
        if "referencia_manual" in data and data["referencia_manual"]:
            referencia = data["referencia_manual"]
        else:
            referencia = f"M{random.randint(10000000, 99999999)}"

        # ✅ Parche: valor seguro
        valor_seguro = _safe_float(data.get("valor"), 0.0)
        valor_formateado = "$ {:,.2f}".format(valor_seguro).replace(",", "X").replace(".", ",").replace("X", ".")

        telefono_raw = data.get("telefono") or ""
        telefono_formateado = (
            telefono_raw if es_comprobante4 or es_comprobante_qr else
            f"{telefono_raw[:3]} {telefono_raw[3:6]} {telefono_raw[6:]}" if telefono_raw.isdigit() and len(telefono_raw) == 10 else telefono_raw
        )

        datos = {
            "telefono": telefono_formateado,
            "nombre": data.get("nombre") or "",
            "valor1": valor_formateado,
            "fecha": fecha,
            "referencia": referencia,
            "disponible": "Disponible",
        }

        if es_comprobante_qr:
            datos = {
                "nombre": data.get("nombre") or "",
                "valor1": valor_formateado,
                "fecha": fecha,
                "referencia": referencia,
                "disponible": "Disponible",
            }

        for campo, texto in datos.items():
            if campo in styles:
                style = styles[campo]
                font = ImageFont.truetype(font_path, style["size"])
                if campo == "valor1":
                    pos_x = style["pos"][0]
                    pos_y = style["pos"][1]
                    draw_text_with_outline(draw, (pos_x, pos_y), str(texto), font, style["color"], "#2e2b33", 2)
                else:
                    draw_text_with_outline(draw, style["pos"], str(texto), font, style["color"], "#2e2b33", 2)

    image.save(output_path)
    return output_path


def generar_comprobante_nuevo(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Fecha
    if "fecha_manual" in data and data["fecha_manual"]:
        fecha = data["fecha_manual"]
    else:
        try:
            meses_es = {
                "january": "enero", "february": "febrero", "march": "marzo", "april": "abril",
                "may": "mayo", "june": "junio", "july": "julio", "august": "agosto",
                "september": "septiembre", "october": "octubre", "november": "noviembre", "december": "diciembre"
            }
            now = datetime.now(pytz.timezone("America/Bogota"))
            mes_en = now.strftime("%B").lower()
            mes = meses_es.get(mes_en, mes_en)
            fecha = now.strftime(f"%d de {mes} de %Y a las %I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")
        except Exception:
            fecha = ""

    # Referencia
    if "referencia_manual" in data and data["referencia_manual"]:
        referencia = data["referencia_manual"]
    else:
        referencia = f"M{random.randint(1000000, 9999999)}"

    # ✅ Parche: valor seguro
    valor_seguro = _safe_float(data.get("valor"), 0.0)
    valor_formateado = "$ {:,.2f}".format(valor_seguro).replace(",", "X").replace(".", ",").replace("X", ".")
    numero_envia_fmt = formatear_telefono_co(data.get("numero_envia") or "")
    nombre_mask = enmascarar_nombre(data.get("nombre") or "")

    datos = {
        "nombre": nombre_mask,
        "valor1": valor_formateado,
        "llave": data.get("llave") or "",
        "banco": data.get("banco") or "",
        "numero_envia": numero_envia_fmt,
        "fecha": fecha,
        "referencia": referencia,
        "disponible": "Disponible",
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            font = ImageFont.truetype(font_path, style.get("size", 22))
            draw_text_with_outline(draw, style["pos"], str(texto), font, style.get("color", "#2e2b33"), "white", 2)

    image.save(output_path)
    return output_path


def generar_comprobante_anulado(data, config):
    base_path = generar_comprobante(data, config)
    return base_path


# ===== Formateo para comprobante de Ahorros =====
def formatear_nombre_ahorros(nombre: str) -> str:
    if not nombre:
        return ""
    return nombre.title()


def formatear_numero_cuenta_ahorros(numero: str) -> str:
    if not numero:
        return ""
    digitos = "".join(ch for ch in numero if ch.isdigit())
    if len(digitos) != 11:
        return numero
    return f"{digitos[:3]} - {digitos[3:9]} - {digitos[9:]}"


def formatear_valor_ahorros(valor_str: str) -> str:
    if not valor_str:
        return ""
    valor_limpio = valor_str.replace(".", "").replace(",", "").replace(" ", "").replace("$", "")
    try:
        valor = int(valor_limpio)
        return f"$ {valor:,}".replace(",", ".")
    except (TypeError, ValueError):
        return valor_str


def formatear_valor_sin_signo(valor_str: str) -> str:
    if not valor_str:
        return ""
    valor_limpio = valor_str.replace(".", "").replace(",", "").replace(" ", "").replace("$", "")
    try:
        valor = int(valor_limpio)
        return f"{valor:,}".replace(",", ".")
    except (TypeError, ValueError):
        return valor_str


def generar_fecha_ahorros() -> str:
    try:
        meses_abrev = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dic"
        }
        now = datetime.now(pytz.timezone("America/Bogota"))
        dia = now.strftime("%d")
        mes = meses_abrev[now.month]
        año = now.year
        hora = now.strftime("%I:%M").lstrip("0")
        periodo = "a. m." if now.hour < 12 else "p. m."
        return f"{dia} {mes} {año} - {hora} {periodo}"
    except Exception:
        return ""


def generar_fecha_bc_qr() -> str:
    try:
        meses_abrev = {
            1: "ene.", 2: "feb.", 3: "mar.", 4: "abr.", 5: "may.", 6: "jun.",
            7: "jul.", 8: "ago.", 9: "sept.", 10: "oct.", 11: "nov.", 12: "dic."
        }
        now = datetime.now(pytz.timezone("America/Bogota"))
        dia = now.strftime("%d")
        mes = meses_abrev[now.month]
        año = now.year
        hora = now.strftime("%I:%M").lstrip("0")
        periodo = "a. m." if now.hour < 12 else "p. m."
        return f"{dia} {mes} {año} - {hora} {periodo}"
    except Exception:
        return ""


def generar_comprobante_ahorros(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    nombre_formateado = formatear_nombre_ahorros(data.get("nombre") or "")
    numero_cuenta_formateado = formatear_numero_cuenta_ahorros(data.get("numero_cuenta") or "")

    # ✅ Parche: valor seguro
    valor_raw = data.get("valor")
    valor_str = str(_safe_int(valor_raw, 0)) if valor_raw is not None else "0"
    valor_formateado = formatear_valor_ahorros(valor_str)

    if "fecha_manual" in data and data["fecha_manual"]:
        fecha_formateada = data["fecha_manual"]
    else:
        fecha_formateada = generar_fecha_ahorros()

    datos = {
        "nombre": nombre_formateado,
        "numero_cuenta": numero_cuenta_formateado,
        "valor": valor_formateado,
        "fecha": fecha_formateada,
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            fuente_campo = style.get("font", font_path)
            font = ImageFont.truetype(fuente_campo, style["size"])
            draw.text(style["pos"], str(texto), font=font, fill=style["color"])

    image.save(output_path)
    return output_path


def generar_comprobante_daviplata(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    if "fecha_manual" in data and data["fecha_manual"]:
        fecha_formateada = data["fecha_manual"]
    else:
        now = datetime.now(pytz.timezone("America/Bogota"))
        fecha_formateada = now.strftime("%d/%m/%Y - %I:%M %p")

    numero_aprobacion = str(random.randint(100000, 999999))

    # ✅ Parche: valor seguro
    valor_seguro = _safe_int(data.get("valor"), 0)
    valor_formateado = f"{valor_seguro:,}".replace(",", ".")

    datos = {
        "nombre": data.get("nombre") or "",
        "recibe": data.get("recibe") or "",
        "valor": valor_formateado,
        "envia": data.get("envia") or "",
        "fecha": fecha_formateada,
        "aprobacion": numero_aprobacion,
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            fuente_campo = style.get("font", font_path)
            font = ImageFont.truetype(fuente_campo, style["size"])
            draw.text(style["pos"], str(texto), font=font, fill=style["color"])

    image.save(output_path)
    return output_path


def generar_comprobante_bc_nq_t(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    numero_cuenta_formateado = formatear_numero_cuenta_ahorros(data.get("telefono") or "")

    # ✅ Parche: valor seguro
    valor_raw = data.get("valor")
    valor_str = str(_safe_int(valor_raw, 0)) if valor_raw is not None else "0"
    valor_formateado = formatear_valor_sin_signo(valor_str)

    if "fecha_manual" in data and data["fecha_manual"]:
        fecha_formateada = data["fecha_manual"]
    else:
        fecha_formateada = generar_fecha_ahorros()

    datos = {
        "numero_cuenta": numero_cuenta_formateado,
        "valor": valor_formateado,
        "fecha": fecha_formateada,
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            fuente_campo = style.get("font", font_path)
            font = ImageFont.truetype(fuente_campo, style["size"])
            draw.text(style["pos"], str(texto), font=font, fill=style["color"])

    image.save(output_path)
    return output_path


def generar_comprobante_bc_qr(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    descripcion_qr = (data.get("descripcion_qr") or "").upper()

    # ✅ Parche: valor seguro
    valor_raw = str(data.get("valor") or "0").replace(".", "").replace(",", "").replace(" ", "")
    if valor_raw.isdigit():
        valor_num = int(valor_raw)
        valor = f"$ {valor_num:,}".replace(",", ".")
    else:
        valor = "$ 0"

    nombre = (data.get("nombre") or "").upper()

    numero_cuenta_raw = (data.get("numero_cuenta") or "").replace(" ", "").replace("-", "")
    if len(numero_cuenta_raw) >= 11:
        numero_cuenta = f"{numero_cuenta_raw[:3]} - {numero_cuenta_raw[3:9]} - {numero_cuenta_raw[9:11]}"
    else:
        numero_cuenta = data.get("numero_cuenta") or ""

    if "fecha_manual" in data and data["fecha_manual"]:
        fecha = data["fecha_manual"]
    else:
        fecha = generar_fecha_bc_qr()

    datos = {
        "punto_venta": descripcion_qr,
        "valor": valor,
        "nombre_enmascarado": nombre,
        "codigo_comercio": numero_cuenta,
        "fecha": fecha,
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            fuente_campo = style.get("font")
            font = ImageFont.truetype(fuente_campo, style["size"])
            draw.text(style["pos"], str(texto), font=font, fill=style["color"])

    image.save(output_path)
    return output_path


def generar_comprobante_nequi_bc(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # ✅ Parche: valor seguro
    valor_seguro = _safe_float(data.get("valor"), 0.0)
    valor_formateado = "$ {:,.2f}".format(valor_seguro).replace(",", "X").replace(".", ",").replace("X", ".")

    numero_cuenta = data.get("numero_cuenta") or ""

    if "referencia_manual" in data and data["referencia_manual"]:
        referencia = data["referencia_manual"]
    else:
        referencia = f"M{random.randint(1000000, 9999999)}"

    if "fecha_manual" in data and data["fecha_manual"]:
        fecha = data["fecha_manual"]
    else:
        meses_es = {
            "january": "enero", "february": "febrero", "march": "marzo", "april": "abril",
            "may": "mayo", "june": "junio", "july": "julio", "august": "agosto",
            "september": "septiembre", "october": "octubre", "november": "noviembre", "december": "diciembre"
        }
        now = datetime.now(pytz.timezone("America/Bogota"))
        mes_en = now.strftime("%B").lower()
        mes = meses_es.get(mes_en, mes_en)
        fecha = now.strftime(f"%d de {mes} de %Y a las %I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")

    datos = {
        "nombre": data.get("nombre") or "",
        "valor": valor_formateado,
        "fecha": fecha,
        "banco": "Bancolombia",
        "numero_cuenta": numero_cuenta,
        "referencia": referencia,
        "disponible": "Disponible"
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            font = ImageFont.truetype(font_path, style["size"])
            draw_text_with_outline(draw, style["pos"], str(texto), font, style["color"], "#2e2b33", 2)

    image.save(output_path)
    return output_path


def generar_comprobante_nequi_ahorros(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # ✅ Parche: valor seguro
    valor_seguro = _safe_float(data.get("valor"), 0.0)
    valor_formateado = "$ {:,.2f}".format(valor_seguro).replace(",", "X").replace(".", ",").replace("X", ".")

    numero_cuenta = data.get("numero_cuenta") or ""

    if "referencia_manual" in data and data["referencia_manual"]:
        referencia = data["referencia_manual"]
    else:
        referencia = f"M{random.randint(1000000, 9999999)}"

    if "fecha_manual" in data and data["fecha_manual"]:
        fecha = data["fecha_manual"]
    else:
        meses_es = {
            "january": "enero", "february": "febrero", "march": "marzo", "april": "abril",
            "may": "mayo", "june": "junio", "july": "julio", "august": "agosto",
            "september": "septiembre", "october": "octubre", "november": "noviembre", "december": "diciembre"
        }
        now = datetime.now(pytz.timezone("America/Bogota"))
        mes_en = now.strftime("%B").lower()
        mes = meses_es.get(mes_en, mes_en)
        fecha = now.strftime(f"%d de {mes} de %Y a las %I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")

    nombre_mask = enmascarar_nombre(data.get("nombre") or "")

    datos = {
        "nombre": nombre_mask,
        "valor": valor_formateado,
        "fecha": fecha,
        "banco": "Bancolombia",
        "numero_cuenta": numero_cuenta,
        "referencia": referencia,
        "disponible": "Disponible"
    }

    for campo, texto in datos.items():
        if campo in styles:
            style = styles[campo]
            font = ImageFont.truetype(font_path, style["size"])
            draw_text_with_outline(draw, style["pos"], str(texto), font, style["color"], "#2e2b33", 2)

    image.save(output_path)
    return output_path


def generar_movimiento_bancolombia(data, config):
    template_path = config["template"]
    output_path = f"gen_{uuid.uuid4().hex}.png"
    styles = config["styles"]
    font_path = config["font"]

    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # ✅ Parche: valor seguro
    valor = abs(_safe_int(data.get("valor"), 0))

    valor_formateado = f"{valor:,}".replace(",", ".") + ","
    decimales = "00"

    font_cop = ImageFont.truetype(font_path, 18)
    font_dolar = ImageFont.truetype(font_path, 24)
    font_valor = ImageFont.truetype(font_path, 23)
    font_dec = ImageFont.truetype(font_path, 17)

    x_decimales = 532
    y_base = 716
    ajuste = 2
    ajuste_dec = 1

    ancho_dec = draw.textlength(decimales, font=font_dec)
    ancho_valor = draw.textlength(valor_formateado, font=font_valor)
    ancho_dolar = draw.textlength("-$", font=font_dolar)
    ancho_cop = draw.textlength("COP", font=font_cop)

    x_valor = x_decimales - ancho_valor + ajuste
    x_dolar = x_valor - ancho_dolar - 5
    x_cop = x_dolar - ancho_cop - 5
    x_dec = x_decimales + ajuste_dec

    color_valor = styles["valor"]["color"]

    draw.text((x_cop, y_base), "COP", font=font_cop, fill=color_valor)
    draw.text((x_dolar, y_base - 2), "-$", font=font_dolar, fill=color_valor)
    draw.text((x_valor, y_base - 1), valor_formateado, font=font_valor, fill=color_valor)
    draw.text((x_dec, y_base + 3), decimales, font=font_dec, fill=color_valor)

    fecha_style = styles.get("fecha")
    if fecha_style:
        font_fecha = ImageFont.truetype(fecha_style.get("font", font_path), fecha_style["size"])
        now = datetime.now(pytz.timezone("America/Bogota"))
        meses_abrev_upper = {
            1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
            7: "JUL", 8: "AGO", 9: "SEPT", 10: "OCT", 11: "NOV", 12: "DIC"
        }
        fecha_texto = f"{now.day:02d} {meses_abrev_upper[now.month]} {now.year}"
        draw.text(fecha_style["pos"], fecha_texto, font=font_fecha, fill=fecha_style["color"])

    nombre_style = styles.get("nombre")
    if nombre_style:
        font_nombre = ImageFont.truetype(nombre_style.get("font", font_path), nombre_style["size"])
        nombre_texto = (data.get("nombre") or "").upper()
        draw.text(nombre_style["pos"], nombre_texto, font=font_nombre, fill=nombre_style["color"])

    image.save(output_path)
    return output_path
