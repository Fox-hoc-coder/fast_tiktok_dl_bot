import logging
import os
import requests
import telebot
from flask import Flask
from threading import Thread

# === 1. WEB SERVER DÙNG ĐỂ PASS PORT CHECK TRÊN RENDER ===
app = Flask('')

@app.route('/')
def home():
    return "Bot TikTok đang hoạt động!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# === 2. THIẾT LẬP TELEGRAM BOT ===
BOT_TOKEN = "8892850570:AAH2A6rEyndq-Uc05x5pYa5zGLpip2UX9lI"
bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_tiktok_video(url: str):
    # Giải nén URL nếu là link rút gọn vt.tiktok.com
    try:
        req = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=8)
        url = req.url
    except Exception as e:
        print(f"Lỗi giải nén URL: {e}")

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
        print(f"Lỗi API TikWM: {e}")
    return {"success": False}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Xin chào! 👋\nHãy gửi cho tôi link video TikTok, tôi sẽ tải video không logo cho bạn!",
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    if "tiktok.com" not in text:
        bot.reply_to(message, "❌ Vui lòng gửi một link TikTok hợp lệ!")
        return

    msg = bot.reply_to(
        message, "⏳ Đang xử lý và tải video, vui lòng chờ trong giây lát..."
    )
    
    try:
        res = get_tiktok_video(text)
        if res["success"] and res.get("video_url"):
            caption = f"🎬 {res['title']}\n👤 Kênh: {res['author']}"
            bot.send_video(message.chat.id, res["video_url"], caption=caption)
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(
                "❌ Không thể tải video này! Có thể link bị lỗi hoặc video ở chế độ riêng tư.",
                message.chat.id,
                msg.message_id,
            )
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        bot.edit_message_text(
            "❌ Đã xảy ra lỗi khi xử lý video. Vui lòng thử lại sau!",
            message.chat.id,
            msg.message_id,
        )


print("Bot đang chạy...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
