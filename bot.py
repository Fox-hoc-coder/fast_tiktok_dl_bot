import os
import requests
import telebot
from flask import Flask, request

BOT_TOKEN = "8892850570:AAH2A6rEyndq-Uc05x5pYa5zGLpip2UX9lI"
# Thay URL này bằng link Web Service thực tế của bạn trên Render
RENDER_URL = "https://fast-tiktok-dl-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_tiktok_video(url: str):
    try:
        req = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=8)
        url = req.url
    except Exception as e:
        print(f"Lỗi URL: {e}")

    api_url = "https://www.tikwm.com/api/"
    payload = {"url": url, "hd": 1}
    try:
        response = requests.post(api_url, data=payload, headers=HEADERS, timeout=12).json()
        if response.get("code") == 0:
            data = response["data"]
            return {
                "success": True,
                "video_url": data.get("play"),
                "title": data.get("title", "TikTok Video"),
                "author": data.get("author", {}).get("nickname", "Unknown"),
            }
    except Exception as e:
        print(f"Lỗi API: {e}")
    return {"success": False}

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + BOT_TOKEN)
    return "Bot Webhook đang chạy!", 200

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Xin chào! 👋\nHãy gửi cho tôi link video TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    if "tiktok.com" not in text:
        bot.reply_to(message, "❌ Vui lòng gửi một link TikTok hợp lệ!")
        return

    msg = bot.reply_to(message, "⏳ Đang xử lý...")
    res = get_tiktok_video(text)
    if res["success"] and res.get("video_url"):
        caption = f"🎬 {res['title']}\n👤 Kênh: {res['author']}"
        bot.send_video(message.chat.id, res["video_url"], caption=caption)
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ Không thể tải video này!", message.chat.id, msg.message_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
