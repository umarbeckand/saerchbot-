import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from io import BytesIO

# === ВАШИ КЛЮЧИ ===
TELEGRAM_TOKEN =  
PIXABAY_API_KEY =   

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Отправь имя знаменитости - получишь фото!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    celebrity_name = update.message.text
    
    await update.message.reply_text(f"🔍 Ищу: {celebrity_name}...")
    
    try:
        # Поиск через Pixabay API
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": celebrity_name,
            "image_type": "photo",
            "per_page": 10,
            "safesearch": True
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data.get("hits") and len(data["hits"]) > 0:
            hits = data["hits"]
            await update.message.reply_text(f"✅ Нашёл {len(hits)} фото! Отправляю первые 3:")
            
            # Отправляем первые 3 фото
            for i, hit in enumerate(hits[:3], 1):
                try:
                    img_url = hit.get("largeImageURL") or hit.get("webformatURL")
                    
                    if img_url:
                        # Скачиваем фото
                        img_response = requests.get(img_url, timeout=10)
                        
                        if img_response.status_code == 200:
                            photo_file = BytesIO(img_response.content)
                            photo_file.name = f'photo_{i}.jpg'
                            
                            await update.message.reply_photo(
                                photo=photo_file,
                                caption=f"📸 {celebrity_name} - Фото {i}"
                            )
                except Exception as e:
                    print(f"Ошибка с фото {i}: {e}")
                    continue
        else:
            await update.message.reply_text("😕 Не нашёл фото. Попробуйте другое имя.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()