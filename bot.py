import logging
import requests
import telebot

BOT_TOKEN = "8892850570:AAH2A6rEyndq-Uc05x5pYa5zGLpip2UX9lI"
bot = telebot.TeleBot(BOT_TOKEN)


def get_tiktok_video(url: str):
    api_url = "https://www.tikwm.com/api/"
    payload = {"url": url, "hd": 1}
    try:
        response = requests.post(api_url, data=payload, timeout=10).json()
        if response.get("code") == 0:
            data = response["data"]
            return {
                "success": True,
                "video_url": data["play"],
                "title": data.get("title", "TikTok Video"),
                "author": data.get("author", {}).get("nickname", "Unknown"),
            }
    except Exception as e:
        print(f"Lỗi API: {e}")
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
    res = get_tiktok_video(text)

    if res["success"]:
        caption = f"🎬 {res['title']}\n👤 Kênh: {res['author']}"
        bot.send_video(message.chat.id, res["video_url"], caption=caption)
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text(
            "❌ Không thể tải video này! Có thể link bị lỗi hoặc video ở chế độ riêng tư.",
            message.chat.id,
            msg.message_id,
        )


print("Bot đang chạy...")
bot.infinity_polling()