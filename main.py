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
TOKEN = "8239033621:AAE_hpwlVUE6mP9oawZyu_o7jp02RXe3Gtk"
ADMIN_ID = 8517391123

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Inicializar sistema de autorización
auth_system = AuthSystem(ADMIN_ID, None) # Quitamos el grupo de la autorización
user_data_store = {}
fecha_manual_mode = {}
referencia_manual_mode = {}

# --- COMANDOS PRINCIPALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if auth_system.is_banned(user_id):
        await update.message.reply_text("🚫 **Acceso Denegado:** Estás baneado del sistema.")
        return

    # Teclado Principal (Diseño actualizado con Emojis)
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

    if user_id in user_data_store:
        data = user_data_store[user_id]
        step = data["step"]
        
        if data["tipo"] == "comprobante1":
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

# --- PANEL DE ADMINISTRACIÓN ---
async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID: return
    await update.message.reply_text("⚙️ **Panel de Control Activo**", parse_mode='Markdown')

# --- INICIO DEL BOT ---
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers corregidos
    app.add_handler(CommandHandler("start", start)) # CAMBIO AQUÍ: start en lugar de start_redirect
    app.add_handler(CommandHandler("comprobante", start))
    app.add_handler(CommandHandler("panel", panel_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot iniciado con éxito y sin restricciones de grupo...")
    app.run_polling()

if __name__ == "__main__":
    main()
