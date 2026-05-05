import os
import logging
import json
import pytz
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

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

# Inicializar sistema de autorización (Sin restricción de grupo)
auth_system = AuthSystem(ADMIN_ID, None)
user_data_store = {}

# --- COMANDOS PRINCIPALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if auth_system.is_banned(user_id):
        await update.message.reply_text("🚫 **Acceso Denegado:** Estás baneado del sistema.")
        return

    # Teclado Principal con Emojis
    keyboard = [
        [KeyboardButton("💳 Nequi"), KeyboardButton("📲 Daviplata")],
        [KeyboardButton("🔍 Nequi QR"), KeyboardButton("🔑 Bre B"), KeyboardButton("❌ Anulado")],
        [KeyboardButton("🏦 Ahorros"), KeyboardButton("📈 Corriente")],
        [KeyboardButton("🔄 BC a NQ"), KeyboardButton("🔳 BC QR")],
        [KeyboardButton("💎 Nequi Corriente"), KeyboardButton("💰 Nequi Ahorros")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👋 **Bienvenido al Generador Pro**\n\nSelecciona el tipo de comprobante que deseas generar hoy:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    mapping = {
        "💳 Nequi": "comprobante1",
        "📲 Daviplata": "comprobante_daviplata",
        "🔍 Nequi QR": "comprobante_qr",
        "🔑 Bre B": "comprobante_nuevo",
        "❌ Anulado": "comprobante_anulado",
        "🏦 Ahorros": "comprobante_ahorros",
        "📈 Corriente": "comprobante_corriente",
        "🔄 BC a NQ": "comprobante_bc_nq_t",
        "🔳 BC QR": "comprobante_bc_qr",
        "💎 Nequi Corriente": "comprobante_nequi_bc",
        "💰 Nequi Ahorros": "comprobante_nequi_ahorros"
    }

    # Si el usuario presiona un botón del menú
    if text in mapping:
        user_data_store[user_id] = {"step": 0, "tipo": mapping[text]}
        prompts = {
            "comprobante1": "👤 **Nombre del destinatario:**",
            "comprobante_daviplata": "👤 **Nombre del destinatario:**",
            "comprobante_qr": "🏪 **Nombre del negocio:**",
            "comprobante_nuevo": "👤 **Nombre del destinatario:**",
            "comprobante_bc_nq_t": "📞 **Número de teléfono (10 dígitos):**"
        }
        await update.message.reply_text(prompts.get(mapping[text], "📝 **Ingresa los datos solicitados:**"), parse_mode='Markdown')
        return

    # Lógica de pasos para Nequi (comprobante1)
    if user_id in user_data_store:
        data = user_data_store[user_id]
        tipo = data["tipo"]
        step = data["step"]

        if tipo == "comprobante1":
            if step == 0:
                data["nombre"] = text
                data["step"] = 1
                await update.message.reply_text("📞 **Número de teléfono (3xx...):**", parse_mode='Markdown')
            elif step == 1:
                if len(text) == 10 and text.startswith("3"):
                    data["telefono"] = text
                    data["step"] = 2
                    await update.message.reply_text("💵 **Valor del envío:**", parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ Número inválido. Debe tener 10 dígitos.")
            elif step == 2:
                data["valor"] = text
                await update.message.reply_text("⏳ **Generando comprobantes, por favor espera...**")
                
                try:
                    # Generar imágenes usando tus utilidades
                    path_comp = generar_comprobante(data["nombre"], data["telefono"], data["valor"])
                    path_mov = generar_movimiento_bancolombia(data["nombre"], data["valor"])

                    # Enviar las imágenes generadas
                    with open(path_comp, 'rb') as photo:
                        await context.bot.send_photo(chat_id=user_id, photo=photo, caption="✅ **Comprobante Nequi Generado**", parse_mode='Markdown')
                    
                    with open(path_mov, 'rb') as photo:
                        await context.bot.send_photo(chat_id=user_id, photo=photo, caption="✅ **Movimiento Bancolombia Generado**", parse_mode='Markdown')

                    await update.message.reply_text("✨ **Proceso finalizado con éxito.**")
                except Exception as e:
                    logging.error(f"Error: {e}")
                    await update.message.reply_text("❌ Error al generar las imágenes. Revisa que las funciones en utils.py funcionen correctamente.")
                
                del user_data_store[user_id]

# --- PANEL DE ADMINISTRACIÓN ---
async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID: return
    await update.message.reply_text("⚙️ **Panel de Control Activo**", parse_mode='Markdown')

# --- INICIO DEL BOT ---
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers corregidos para evitar el NameError
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CommandHandler("comprobante", start))
    app.add_handler(CommandHandler("panel", panel_command))
    
    # Manejador de mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot iniciado con éxito. Error de redirección corregido y flujo de generación activo.")
    app.run_polling()

if __name__ == "__main__":
    main()
