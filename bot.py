import io
import os
import requests
import telebot
import yt_dlp
from flask import Flask, request

BOT_TOKEN = "8892850570:AAH2A6rEyndq-Uc05x5pYa5zGLpip2UX9lI"
RENDER_URL = "https://fast-tiktok-dl-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_tiktok(url: str):
    # Tự động giải nén URL nếu là link vt.tiktok.com
    try:
        req = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=8)
        url = req.url
    except Exception as e:
        print(f"Lỗi giải nén URL: {e}")

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")
            title = info.get("title", "TikTok Video")
            author = info.get("uploader", "Unknown")

            if video_url:
                # Tải nội dung video về RAM dưới dạng bytes
                res = requests.get(video_url, headers=HEADERS, timeout=20)
                if res.status_code == 200:
                    video_bytes = io.BytesIO(res.content)
                    video_bytes.name = "video.mp4"
                    return {
                        "success": True,
                        "video_data": video_bytes,
                        "title": title,
                        "author": author
                    }
    except Exception as e:
        print(f"Lỗi yt-dlp: {e}")
        
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

    msg = bot.reply_to(message, "⏳ Đang xử lý và tải video...")
    res = download_tiktok(text)
    
    if res["success"]:
        caption = f"🎬 {res['title']}\n👤 Kênh: {res['author']}"
        bot.send_video(message.chat.id, res["video_data"], caption=caption)
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ Không thể tải video này! Có thể link bị lỗi hoặc video riêng tư.", message.chat.id, msg.message_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
