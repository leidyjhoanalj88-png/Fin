import os
import logging
import json
import pytz
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# Importaciones de configuración y utilidades (asegúrate que estos archivos existan)
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
ALLOWED_GROUP = -1003832824723  # ID del grupo permitido
REQUIRED_GROUP_ID = -1003832824723

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Inicializar sistema de autoridación
auth_system = AuthSystem(ADMIN_ID, ALLOWED_GROUP)
user_data_store = {}
fecha_manual_mode = {}
referencia_manual_mode = {}

# --- UTILIDADES ---
async def is_member_of_group(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_GROUP_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# --- COMANDOS PRINCIPALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if auth_system.is_banned(user_id):
        await update.message.reply_text("🚫 **Acceso Denegado:** Estás baneado del sistema.")
        return

    if not await is_member_of_group(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("📲 Unirse al Grupo", url="https://t.me/Nequiibotgv")]]
        await update.message.reply_text(
            "⚠️ **¡ALTO AHÍ!**\n\nPara usar este bot, debes ser miembro de nuestro grupo oficial.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    # Teclado Principal
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
    
    # Mapeo de botones a tipos de datos
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
        # Reiniciar flujo para el usuario
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

    # Lógica de pasos (ejemplo simplificado para Nequi)
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
                    await update.message.reply_text("❌ Número inválido. Debe tener 10 dígitos y empezar por 3.")
            elif step == 2:
                # Aquí iría la generación del PDF/Imagen
                await update.message.reply_text("⏳ **Generando comprobante...**")
                # ... (resto de tu lógica de generación) ...
                del user_data_store[user_id]

# --- PANEL DE ADMINISTRACIÓN MEJORADO ---
async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID: return

    stats = auth_system.get_stats()
    status_bot = "🟢 ONLINE" if auth_system.gratis_mode else "🔴 PREMIUM"

    message = (
        "⚙️ **PANEL DE CONTROL SUPREMO**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Estado:** {status_bot}\n"
        f"👥 **Usuarios:** {stats['total_authorized']}\n"
        f"🚫 **Baneados:** {stats['total_banned']}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Utilice los botones inferiores para gestionar el bot:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔓 Abrir Gratis", callback_data="panel_gratis"),
         InlineKeyboardButton("🔒 Cerrar Bot", callback_data="panel_off")],
        [InlineKeyboardButton("📊 Estadísticas Detalladas", callback_data="panel_stats")]
    ]
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# --- INICIO DEL BOT ---
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_redirect))
    app.add_handler(CommandHandler("comprobante", start))
    app.add_handler(CommandHandler("panel", panel_command))
    app.add_handler(CommandHandler("fechas", fechas_command))
    app.add_handler(CommandHandler("refes", refes_command))
    
    # Manejador de mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(panel_callback, pattern="^panel_"))
    app.add_handler(CallbackQueryHandler(apk_precios_callback, pattern="^apk_precios$"))

    print("🚀 Bot iniciado con éxito...")
    app.run_polling()

if __name__ == "__main__":
    main()
