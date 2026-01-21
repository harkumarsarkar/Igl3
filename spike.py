===============================

Telegram Admin Approval Bot

Tested for Termux + Python 3.12

Library: python-telegram-bot==20.7

===============================

import sqlite3 from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

======== CONFIG ========

BOT_TOKEN = "7756376632:AAFdH6uGmSBOKWjFJrJEvO_LMC6b8k2sfos" ADMIN_ID = 1944789569  # replace with your Telegram numeric ID

======== DATABASE ========

conn = sqlite3.connect("users.db", check_same_thread=False) cursor = conn.cursor()

cursor.execute( """ CREATE TABLE IF NOT EXISTS users ( user_id INTEGER PRIMARY KEY, status TEXT ) """ ) conn.commit()

======== HELPER FUNCTIONS ========

def get_status(user_id: int): cursor.execute("SELECT status FROM users WHERE user_id=?", (user_id,)) row = cursor.fetchone() return row[0] if row else None

def set_status(user_id: int, status: str): cursor.execute( "REPLACE INTO users (user_id, status) VALUES (?, ?)", (user_id, status) ) conn.commit()

======== PAYMENT CONFIG ========

PAY_QR_IMAGE = "payment_qr.jpg"  # optional QR image file PAY_AMOUNT_TEXT = "₹99 Pay karke screenshot bhejein" AUTO_APPROVE_SECONDS = 60

Files for each menu option

FILES = { "normal": "normal_headshot.zip", "youtube": "youtube_pro_headshot.zip", "antenna": "antenna_headshot.zip", "brutal": "full_brutal_max.zip" }  # jo file deni hai

======== ADMIN REMOVE USER COMMAND ========

/remove user_id  -> user ka access remove karega

======== COMMANDS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user status = get_status(user.id)

if status == "approved":
    await update.message.reply_text("✅ Aap approved ho. /menu likhiye.")
    return

if status == "pending":
    await update.message.reply_text("⏳ Aapka request pending hai.")
    return

await update.message.reply_text(
    "💳 Access ke liye payment required. /pay likhiye aur screenshot bhejiye."
)

async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user if get_status(user.id) == "approved": await update.message.reply_text("✅ Aap already approved ho. /menu") return

set_status(user.id, "pending")
await update.message.reply_text(
    f"{PAY_AMOUNT_TEXT}

Payment ke baad screenshot (photo) bhejiye." )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user if get_status(user.id) != "pending": await update.message.reply_text("❌ Aap pending list me nahi ho.") return

# Admin ko forward
await context.bot.send_message(
    chat_id=ADMIN_ID,
    text=f"💳 Payment Screenshot Received

User: {user.full_name} ID: {user.id}" ) await update.message.forward(chat_id=ADMIN_ID)

await update.message.reply_text(
    f"⏱️ Screenshot mil gaya. {AUTO_APPROVE_SECONDS} seconds me auto-approval ho jayega."
)

# Auto approve after delay
context.job_queue.run_once(auto_approve_job, AUTO_APPROVE_SECONDS, data=user.id)

async def auto_approve_job(context: ContextTypes.DEFAULT_TYPE): user_id = context.job.data if get_status(user_id) == "pending": set_status(user_id, "approved") await context.bot.send_message(user_id, "🎉 Payment verified! Aap approved ho gaye. /menu")

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer()(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer()

if query.from_user.id != ADMIN_ID:
    await query.edit_message_text("❌ Aap admin nahi ho.")
    return

action, user_id = query.data.split("_")
user_id = int(user_id)

if action == "approve":
    set_status(user_id, "approved")
    await context.bot.send_message(user_id, "🎉 Aap approve ho gaye ho!")
    await query.edit_message_text(f"✅ User {user_id} approved")

elif action == "reject":
    set_status(user_id, "rejected")
    await context.bot.send_message(user_id, "❌ Aapka request reject ho gaya")
    await query.edit_message_text(f"🚫 User {user_id} rejected")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): if get_status(update.effective_user.id) != "approved": await update.message.reply_text("❌ Aap approved nahi ho.") return

await update.message.reply_text(
    "ℹ️ Commands:\n"
    "/start – Start bot\n"
    "/help – Help"
)

async def approved_users(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != ADMIN_ID: return

cursor.execute("SELECT user_id FROM users WHERE status='approved'")
users = cursor.fetchall()

if not users:
    await update.message.reply_text("No approved users")
    return

text = "✅ Approved Users:\n" + "\n".join(str(u[0]) for u in users)
await update.message.reply_text(text)

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != ADMIN_ID: await update.message.reply_text("❌ Sirf admin use kar sakta hai.") return

if not context.args:
    await update.message.reply_text("Usage: /remove USER_ID")
    return

try:
    user_id = int(context.args[0])
except ValueError:
    await update.message.reply_text("❌ Invalid user id")
    return

cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
conn.commit()

await update.message.reply_text(f"✅ User {user_id} removed successfully")

async def pending_users(update: Update, context: ContextTypes.DEFAULT_TYPE):(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != ADMIN_ID: return

cursor.execute("SELECT user_id FROM users WHERE status='pending'")
users = cursor.fetchall()

if not users:
    await update.message.reply_text("No pending users")
    return

text = "⏳ Pending Users:\n" + "\n".join(str(u[0]) for u in users)
await update.message.reply_text(text)

======== MAIN ========

def menu_keyboard(): return InlineKeyboardMarkup([ [InlineKeyboardButton("📁 Get File", callback_data="get_file")], [InlineKeyboardButton("🤖 🧠 Normal Headshot 🎯 YouTube Pro Headshot 📡 Antenna Headshot 🔥 Full Brutal Max 📞 Contact Owner (@Yourspike)", callback_data="help_menu")] ])

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): if get_status(update.effective_user.id) != "approved": await update.message.reply_text("❌ Aap approved nahi ho.") return

await update.message.reply_text(
    "📂 Main Menu (Floating Options)",
    reply_markup=menu_keyboard()
)

async def menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer()

if get_status(query.from_user.id) != "approved":
    await query.edit_message_text("❌ Aap approved nahi ho.")
    return

if query.data == "get_file":
    try:
        await context.bot.send_document(chat_id=query.from_user.id, document=open(FILE_TO_SEND, "rb"))
    except Exception:
        await context.bot.send_message(query.from_user.id, "❌ File not found on server.")

elif query.data == "help_menu":
    await query.edit_message_text(
        "ℹ️ Help:

Payment ke baad auto approval hota hai aur file milti hai." ): query = update.callback_query await query.answer()

if query.data == "help_menu":
    await query.edit_message_text(
        "ℹ️ Menu Help:

" "🤖 Open Public Bot – Dusra public bot open karega " "Admin approval ke baad hi menu dikhega" )

def main(): app = ApplicationBuilder().token(BOT_TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("menu", show_menu)) app.add_handler(CommandHandler("pay", pay_cmd)) app.add_handler(CallbackQueryHandler(admin_action, pattern="^(approve|reject)")) app.add_handler(CallbackQueryHandler(menu_actions, pattern="^(get_file|help_menu)$")), pattern="^(approve|reject)")) app.add_handler(CallbackQueryHandler(menu_actions, pattern="^help_menu$")) print("🤖 Bot running...") app.run_polling()

if name == "main": main()
