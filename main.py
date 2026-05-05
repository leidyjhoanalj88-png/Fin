import os
import logging
import json
import pytz
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Importaciones de configuración y utilidades
from config import *
from utils import (
    generar_comprobante, generar_comprobante_nuevo, generar_comprobante_anulado, 
    enmascarar_nombre, generar_comprobante_ahorros, generar_comprobante_daviplata, 
    generar_comprobante_bc_nq_t, generar_comprobante_bc_qr, generar_comprobante_nequi_bc, 
    generar_comprobante_nequi_ahorros, generar_movimiento_bancolombia
)
from auth_system import AuthSystem

# --- CONFIGURACIÓN CRÍTICA ---
TOKEN = "7928537663:AAHEfHZFq1wJJpaG0Hz2FNILakAtyN1fmSU"
ADMIN_ID = 8517391123

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

auth_system = AuthSystem(ADMIN_ID, None)
user_data_store = {}

# --- COMANDOS PRINCIPALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if auth_system.is_banned(user_id):
        await update.message.reply_text("🚫 Acceso Denegado.")
        return

    keyboard = [
        [KeyboardButton("💳 Nequi"), KeyboardButton("📲 Daviplata")],
        [KeyboardButton("🔍 Nequi QR"), KeyboardButton("🔑 Bre B"), KeyboardButton("❌ Anulado")],
        [KeyboardButton("🏦 Ahorros"), KeyboardButton("📈 Corriente")],
        [KeyboardButton("🔄 BC a NQ"), KeyboardButton("🔳 BC QR")],
        [KeyboardButton("💎 Nequi Corriente"), KeyboardButton("💰 Nequi Ahorros")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 **Bienvenido al Generador Pro**\nSelecciona una opción:", reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    mapping = {
        "💳 Nequi": "comprobante1",
        "📲 Daviplata": "comprobante_daviplata",
        "🔍 Nequi QR": "comprobante_qr",
        "🔑 Bre B": "comprobante_nuevo"
    }

    if text in mapping:
        user_data_store[user_id] = {"step": 0, "tipo": mapping[text]}
        await update.message.reply_text("👤 **Nombre del destinatario:**", parse_mode='Markdown')
        return

    if user_id in user_data_store:
        data = user_data_store[user_id]
        
        if data["tipo"] == "comprobante1":
            if data["step"] == 0:
                data["nombre"] = text
                data["step"] = 1
                await update.message.reply_text("📞 **Número de teléfono:**", parse_mode='Markdown')
            elif data["step"] == 1:
                data["telefono"] = text
                data["step"] = 2
                await update.message.reply_text("💵 **Valor del envío:**", parse_mode='Markdown')
            elif data["step"] == 2:
                # Limpiar el valor para evitar errores matemáticos
                valor_limpio = text.replace("$", "").replace(".", "").replace(",", "").strip()
                data["valor"] = valor_limpio
                
                msg_espera = await update.message.reply_text("⏳ **Generando comprobantes...**")
                
                try:
                    # CONFIGURACIONES PARA LAS FUNCIONES DE UTILS.PY
                    config_nequi = {
                        "template": "nequi_template.png",
                        "font": "font.ttf",
                        "output": "comprobante_generado.png",
                        "styles": {
                            "nombre": {"pos": (114, 420), "size": 33, "color": "#2e2b33"},
                            "telefono": {"pos": (114, 465), "size": 28, "color": "#2e2b33"},
                            "valor1": {"pos": (114, 530), "size": 45, "color": "#ff007a"},
                            "fecha": {"pos": (114, 600), "size": 22, "color": "#2e2b33"},
                            "referencia": {"pos": (114, 650), "size": 22, "color": "#2e2b33"}
                        }
                    }
                    
                    config_mov = {
                        "template": "bancolombia_mov.png",
                        "font": "font.ttf",
                        "styles": {
                            "nombre": {"pos": (50, 680), "size": 20, "color": "#000000"},
                            "valor": {"pos": (400, 715), "size": 22, "color": "#333333"}
                        }
                    }

                    # Llamada a tus funciones (pasando data y config como pide tu utils.py)
                    path_comp = generar_comprobante(data, config_nequi)
                    path_mov = generar_movimiento_bancolombia(data, config_mov)

                    # Envío de archivos si existen
                    if os.path.exists(path_comp):
                        with open(path_comp, 'rb') as photo:
                            await context.bot.send_photo(chat_id=user_id, photo=photo, caption="✅ **Comprobante Nequi**")
                    
                    if os.path.exists(path_mov):
                        with open(path_mov, 'rb') as photo:
                            await context.bot.send_photo(chat_id=user_id, photo=photo, caption="✅ **Movimiento Bancolombia**")

                    await msg_espera.delete()
                except Exception as e:
                    logging.error(f"Error: {e}")
                    await update.message.reply_text(f"❌ Error técnico: {e}")
                
                del user_data_store[user_id]

# --- INICIO ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("comprobante", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot iniciado correctamente...")
    app.run_polling()

if __name__ == "__main__":
    main()
