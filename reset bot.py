from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest
import requests, uuid, random, string

# ---------- New Instagram Reset ----------
class Reset:
    def __init__(self):
        self.url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
        self.headers = {
            "user-agent": "Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; {rand}/{rand}; {rand}; {rand}; en_GB;)".format(
                rand=''.join(random.choices(string.ascii_lowercase + string.digits, k=16)))
        }

    def send(self, email):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        dev_id = str(uuid.uuid4())
        guid = str(uuid.uuid4())

        # email or username
        data = {"_csrftoken": token, "guid": guid, "device_id": dev_id}
        if "@" in email:
            data["user_email"] = email
        else:
            data["username"] = email

        resp = requests.post(self.url, headers=self.headers, data=data)

        # ---- REAL CHECK ----
        if resp.status_code == 200:
            try:
                json_resp = resp.json()
                if "obfuscated_email" in json_resp:   # reset actually sent
                    return {"status": "ok"}
            except ValueError:
                pass
        return {"status": "fail"}

# ---------- Telegram Bot ----------
TOKEN = "8492222698:AAHitEup6XYzox9LThSXEpAdJCnNzkPgGf0"
BOT_USERNAME = "IGBACKxBOT"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        try:
            await update.message.delete()
        except BadRequest:
            pass
        link = f"http://t.me/{BOT_USERNAME}?start=start"
        await context.bot.send_message(chat_id=update.message.chat.id, text=f"🤖 Write me in private: [Click here]({link})", parse_mode="Markdown")
        return
    keyboard = [[KeyboardButton("reset")]]
    await update.message.reply_text("🤖 Instagram Reset Bot Press Button:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 *Instagram Reset*\n\nCommands:\n• /start - Start\n• /help - Help\n• /reset <email> - Quick\n\nUse: Click button → Enter email → Done", parse_mode="Markdown")

async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usage: `/reset <email or username>`", parse_mode="Markdown")
        return
    email = " ".join(context.args).strip()
    reset = Reset()
    result = reset.send(email)
    if result and result.get("status") == "ok":
        await update.message.reply_text(f"✅ Done! Check \"{email}\"")
    else:
        await update.message.reply_text(f'❌ Failed: "{email}"')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "reset":
        await update.message.reply_text("📧 Enter username/email:")
        context.user_data['expecting_input'] = True
        return
    if context.user_data.get('expecting_input'):
        email = text
        reset = Reset()
        result = reset.send(email)
        if result and result.get("status") == "ok":
            await update.message.reply_text(f"✅ Done! Check \"{email}\"")
        else:
            await update.message.reply_text(f'❌ Failed: "{email}\"')
        context.user_data['expecting_input'] = False
        return
    await update.message.reply_text("🤖 Use commands or button:\n• `/start` - Start\n• `/help` - Help\n• `/reset <email>` - Quick", parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
