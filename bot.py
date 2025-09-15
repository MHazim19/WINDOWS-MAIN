import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Konfigurasi dasar
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Ambil konfigurasi dari environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ACTION_PAT = os.getenv("ACTION_PAT")
GITHUB_USER = os.getenv("USERNAME_GH") # Disesuaikan dengan nama secret Anda
CONTROLLER_REPO = "windows-main"

def trigger_workflow(workflow_file: str, target_range: str):
    """Fungsi generik untuk memicu workflow di repo windows-main."""
    
    url = f"https://api.github.com/repos/{GITHUB_USER}/{CONTROLLER_REPO}/actions/workflows/{workflow_file}/dispatches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {ACTION_PAT}"
    }
    data = {
        "ref": "main",
        "inputs": { "target_range": target_range }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 204

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /run <target>."""
    target = context.args[0] if context.args else "ALL"
    await update.message.reply_text(f"🚀 Perintah diterima! Memicu workflow untuk target: `{target}`...", parse_mode='Markdown')
    
    success = trigger_workflow("main.yml", target)
    if not success:
        await update.message.reply_text("❌ Gagal memicu workflow utama. Cek kembali konfigurasi.", parse_mode='Markdown')

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /stop <target>."""
    target = context.args[0] if context.args else "ALL"
    await update.message.reply_text(f"🛑 Perintah diterima! Menghentikan sesi RDP untuk target: `{target}`...", parse_mode='Markdown')
    
    success = trigger_workflow("stop_workflow.yml", target)
    if success:
        await update.message.reply_text("Perintah penghentian telah dikirim. Anda akan menerima konfirmasi untuk setiap sesi.", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Gagal memicu workflow penghentian. Cek kembali konfigurasi.", parse_mode='Markdown')

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("stop", stop_command))

    logging.info("Bot controller is running with /run and /stop commands...")
    application.run_polling()

if __name__ == "__main__":
    main()
