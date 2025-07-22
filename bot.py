
import os
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import uuid

def convert_txt_to_vcf(txt_path, vcf_path):
    with open(txt_path, 'r') as txt_file, open(vcf_path, 'w') as vcf_file:
        for i, line in enumerate(txt_file):
            number = line.strip()
            if not number:
                continue
            vcf_file.write("BEGIN:VCARD\n")
            vcf_file.write("VERSION:3.0\n")
            vcf_file.write(f"FN:Contact {i+1}\n")
            vcf_file.write(f"TEL:{number}\n")
            vcf_file.write("END:VCARD\n\n")

def convert_vcf_to_txt(vcf_path, txt_path):
    with open(vcf_path, 'r') as vcf_file, open(txt_path, 'w') as txt_file:
        for line in vcf_file:
            if line.startswith("TEL"):
                txt_file.write(line.replace("TEL:", "").strip() + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Bot Telegram Railway aktif. Gunakan /to_vcf atau /to_txt.")

async def to_vcf_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Silakan kirim file .txt.")
        return
    file = await update.message.document.get_file()
    txt_path = f"/tmp/{file.file_id}.txt"
    vcf_path = f"/tmp/{file.file_id}.vcf"
    await file.download_to_drive(txt_path)
    convert_txt_to_vcf(txt_path, vcf_path)
    await update.message.reply_document(document=InputFile(vcf_path), filename="converted.vcf")

async def to_txt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Silakan kirim file .vcf.")
        return
    file = await update.message.document.get_file()
    vcf_path = f"/tmp/{file.file_id}.vcf"
    txt_path = f"/tmp/{file.file_id}.txt"
    await file.download_to_drive(vcf_path)
    convert_vcf_to_txt(vcf_path, txt_path)
    await update.message.reply_document(document=InputFile(txt_path), filename="converted.txt")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise Exception("Env var TELEGRAM_BOT_TOKEN tidak ditemukan!")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("to_vcf", to_vcf_handler))
    app.add_handler(CommandHandler("to_txt", to_txt_handler))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("txt"), to_vcf_handler))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("vcf"), to_txt_handler))
    print("Bot aktif...")
    app.run_polling()

if __name__ == '__main__':
    main()
