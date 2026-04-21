import os
import requests
import logging

# Ensure logging is enabled so we can trace when token is missing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TelegramNotifier:
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        
        if not self.token or not self.chat_id:
            logging.warning("Telegram credentials (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID) are missing. Notifications will run in mock mode.")

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Sends a message to a Telegram chat. If tokens are not provided, it prints the payload locally for debugging.
        """
        if not self.token or not self.chat_id:
            logging.info(f"[MOCK TELEGRAM NOTIFICATION] Mode: {parse_mode}\nPayload:\n{text}")
            return True

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logging.info("Telegram message sent successfully.")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Telegram message: {e}")
            if e.response is not None:
                logging.error(f"Response: {e.response.text}")
            return False
