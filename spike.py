import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "7756376632:AAFdH6uGmSBOKWjFJrJEvO_LMC6b8k2sfos"
ADMIN_ID = 1944789569  

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    status TEXT
)
""")
conn.commit()

def get_status(user_id):
    cursor.execute("SELECT status FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def set_status(user_id, status):
    cursor.execute(
        "REPLACE INTO users (user_id, status) VALUES (?, ?)",
        (user_id, status)
    )
    conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    status = get_status(user.id)

    if status == "approved":
        await update.message.reply_text("✅ Aap approved ho.")
        return

    if status == "pending":
        await update.message.reply_text("⏳ Aapka request pending hai.")
        return

    set_status(user.id, "pending")

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
    ]]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🛂 New User\nName: {user.full_name}\nID: {user.id}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ Admin approval ka wait karein.")

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if action == "approve":
        set_status(user_id, "approved")
        await context.bot.send_message(user_id, "🎉 Aap approved ho gaye ho!")
        await query.edit_message_text("✅ Approved")

    elif action == "reject":
        set_status(user_id, "rejected")
        await context.bot.send_message(user_id, "❌ Request reject ho gaya")
        await query.edit_message_text("🚫 Rejected")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(admin_action))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()