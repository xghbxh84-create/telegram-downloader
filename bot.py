import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "স্বাগতম! 👋\n"
        "আমি আপনাকে Facebook, YouTube এবং TikTok থেকে ভিডিও ডাউনলোড করতে সাহায্য করতে পারি।\n"
        "ডাউনলোড করতে যেকোনো ভিডিওর লিঙ্ক আমাকে পাঠান।"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("দয়া করে একটি সঠিক ভিডিও লিঙ্ক (URL) পাঠান।")
        return

    status_message = await update.message.reply_text("ভিডিওটি প্রসেস করা হচ্ছে... দয়া করে অপেক্ষা করুন। ⏳")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                filename = os.path.splitext(filename)[0] + ".mp4"

        await status_message.edit_text("ভিডিওটি টেলিগ্রামে আপলোড করা হচ্ছে... 📤")
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption=f"ডাউনলোড সম্পন্ন হয়েছে! \n\nশিরোনাম: {info.get('title', 'Video')}")
        
        if os.path.exists(filename):
            os.remove(filename)
        await status_message.delete()

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_message.edit_text("দুঃখিত, ভিডিওটি ডাউনলোড করা যায়নি। লিঙ্কটি চেক করুন অথবা ভিডিওর সাইজ খুব বড় (৫০ MB এর বেশি) হতে পারে।")
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN পাওয়া যায়নি!")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("বটটি সফলভাবে চালু হয়েছে...")
    application.run_polling()

if __name__ == '__main__':
    main()
