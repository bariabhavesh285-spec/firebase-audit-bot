import telebot
import zipfile
import re
import os
import requests

# Telegram Bot Token
BOT_TOKEN = "8805502590:AAHj45cO2uY_TetaAtFukQMVv2XHZkrmxa8"
bot = telebot.TeleBot(BOT_TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

# Firebase Configuration Regex Patterns
FIREBASE_DB_PATTERN = r"https://[a-zA-Z0-9-]+\.firebaseio\.com"
STORAGE_PATTERN = r"[a-zA-Z0-9-]+\.appspot\.com"
API_KEY_PATTERN = r"AIzaSy[a-zA-Z0-9-_]{33}"
PROJECT_ID_PATTERN = r'"project_id"\s*:\s*"([^"]+)"|([a-zA-Z0-9-]+)\.firebaseio\.com'
APP_ID_PATTERN = r"1:[0-9]+:android:[a-f0-9]+"

def advanced_firebase_audit(db_url):
    clean_url = db_url.strip()
    status_report = ""
    try:
        read_url = f"{clean_url}/.json?shallow=true"
        read_res = requests.get(read_url, timeout=5)
        if read_res.status_code == 200:
            status_report += "🔓 PUBLIC READ: Enabled (Authentication rules are open).\n"
        elif read_res.status_code in [401, 403]:
            status_report += "🔒 SECURE READ: Protected (Requires authentication token).\n"
        else:
            status_report += f"ℹ️ READ STATUS: Server returned code {read_res.status_code}\n"
    except Exception:
        status_report += "⚠️ READ STATUS: Connection timeout during security check.\n"
    return status_report

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    file_name = message.document.file_name
    if not file_name.endswith('.apk'):
        bot.reply_to(message, "❌ Please sirf ek .apk file send karein.")
        return

    msg = bot.reply_to(message, "📥 APK Receive ho gayi hai. Firebase parameters aur configuration metadata scan ho raha hai...")

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        apk_path = "temp_app.apk"
        with open(apk_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        found_dbs = set()
        found_buckets = set()
        found_api_keys = set()
        found_project_ids = set()
        found_app_ids = set()

        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            for file_in_zip in zip_ref.namelist():
                if file_in_zip.endswith('.arsc') or file_in_zip.endswith('.dex') or file_in_zip.endswith('google-services.json'):
                    try:
                        with zip_ref.open(file_in_zip) as f:
                            content = f.read()
                            text_content = content.decode('utf-8', errors='ignore')

                            for match in re.findall(FIREBASE_DB_PATTERN, text_content):
                                found_dbs.add(match.strip())
                            for match in re.findall(STORAGE_PATTERN, text_content):
                                found_buckets.add(match.strip())
                            for match in re.findall(API_KEY_PATTERN, text_content):
                                found_api_keys.add(match.strip())
                            for match in re.findall(APP_ID_PATTERN, text_content):
                                found_app_ids.add(match.strip())
                            for match in re.findall(PROJECT_ID_PATTERN, text_content):
                                p_id = match[0] if match[0] else match[1]
                                if p_id:
                                    found_project_ids.add(p_id.strip())
                    except Exception:
                        continue

        if os.path.exists(apk_path):
            os.remove(apk_path)

        if found_dbs or found_api_keys or found_project_ids or found_app_ids or found_buckets:
            response_text = "🔍 **FIREBASE CONFIGURATION REPORT** 🔍\n\n"
            if found_dbs:
                response_text += "📁 **Database Endpoints:**\n"
                for db in found_dbs:
                    audit = advanced_firebase_audit(db)
                    response_text += f"🔗 URL: {db}\n🛡️ Security: {audit}\n"
            if found_api_keys:
                response_text += "🔑 **API Tokens / Keys Found:**\n"
                for key in found_api_keys:
                    response_text += f"`{key}`\n"
                response_text += "\n"
            if found_project_ids:
                response_text += "🆔 **Project IDs Found:**\n"
                for pid in found_project_ids:
                    response_text += f"`{pid}`\n"
                response_text += "\n"
            if sorted(list(found_app_ids)):
                response_text += "📱 **App IDs Found:**\n"
                for aid in found_app_ids:
                    response_text += f"`{aid}`\n"
                response_text += "\n"
            if stroke := found_buckets:
                response_text += "📦 **Storage Buckets (Bucket ID):**\n"
                for bucket in found_buckets:
                    response_text += f"`{bucket}`\n"
                response_text += "\n"
            bot.edit_message_text(response_text, message.chat.id, msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("✅ Scan complete! Koi Firebase core configuration parameters nahi mile.", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Scan ke dauran koi error aayi: {str(e)}", message.chat.id, msg.message_id)
        if os.path.exists(apk_path):
            os.remove(apk_path)

print("Bot chal raha hai...")
bot.infinity_polling()
