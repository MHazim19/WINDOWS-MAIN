import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Konfigurasi dasar
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Ambil konfigurasi dari environment (secrets di GitHub Actions)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_PAT = os.getenv("ACTION_PAT")
GITHUB_USER = os.getenv("GITHUB_USER")
CONTROLLER_REPO = "windows-main"
WORKFLOW_FILE_NAME = "main.yml"

def trigger_main_workflow(target_range: str):
    """Memicu workflow di repo windows-main."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{CONTROLLER_REPO}/actions/workflows/{WORKFLOW_FILE_NAME}/dispatches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_PAT}"
    }
    data = {
        "ref": "main",
        "inputs": {
            "target_range": target_range
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 204:
        logging.info(f"Successfully triggered controller workflow for target: {target_range}")
        return True, f"✅ Workflow utama berhasil dipicu untuk target: `{target_range}`"
    else:
        logging.error(f"Failed to trigger workflow. Status: {response.status_code}, Response: {response.text}")
        return False, f"❌ Gagal memicu workflow utama. Cek kembali konfigurasi."

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /run <target>."""
    if context.args:
        target = context.args[0]
    else:
        target = "ALL"
    await update.message.reply_text(f"🚀 Perintah diterima! Memicu workflow untuk target: `{target}`...", parse_mode='Markdown')
    success, message = trigger_main_workflow(target)
    await update.message.reply_text(message, parse_mode='Markdown')

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("run", run_command))
    logging.info("Bot server is running inside GitHub Actions...")
    # Mulai bot untuk mendengarkan pesan tanpa henti
    application.run_polling()

if __name__ == "__main__":
    main()
