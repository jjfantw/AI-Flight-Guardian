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
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code != 200:
                logging.error(f"Telegram API Error (Status {response.status_code}): {response.text}")
                return False
            logging.info("Telegram message sent successfully.")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while sending Telegram message: {e}")
            return False

    def send_daily_summary(self, task: dict, trend_data: dict, is_lowest: bool = False) -> bool:
        """Sends a daily summary of the market trends for a task."""
        search_url = trend_data.get("search_url", "https://www.google.com/travel/flights")
        
        alarm_prefix = "🚨 *[ALARM: 創新低價！]* 🚨\n" if is_lowest else ""
        
        msg = (
            f"{alarm_prefix}📊 *Flight Guardian Daily Summary*\n"
            f"**Task**: `{task.get('name')}`\n"
            f"💰 Today's Lowest: `{trend_data.get('today_lowest')} TWD`\n"
            f"📈 Hist. Highest: `{trend_data.get('historical_highest')} TWD`\n"
            f"📉 Hist. Lowest: `{trend_data.get('historical_lowest')} TWD`\n"
            f"📊 Hist. Average: `{trend_data.get('historical_avg', 0):.0f} TWD`"
            f"\n\n[👉 Go to Google Flights]({search_url})"
        )
        return self.send_message(msg)

    def send_no_flights_summary(self, task: dict, trend_data: dict) -> bool:
        """Sends a summary indicating no flights were found."""
        msg = (
            f"📭 *Flight Guardian Daily Summary*\n"
            f"**Task**: `{task.get('name')}`\n"
            f"⚠️ *本日無符合條件之機票進場*\n"
            f"📈 Hist. Highest: `{trend_data.get('historical_highest')} TWD`\n"
            f"📉 Hist. Lowest: `{trend_data.get('historical_lowest')} TWD`\n"
            f"📊 Hist. Average: `{trend_data.get('historical_avg', 0):.0f} TWD`"
        )
        return self.send_message(msg)

    def send_price_drop_alert(self, task: dict, flight_data: dict) -> bool:
        """Sends an urgent low price drop alert."""
        search_url = flight_data.get("search_url", "https://www.google.com/travel/flights")
        msg = (
            f"🚨 *PRICE DROP ALERT!* 🚨\n"
            f"**Task**: `{task.get('name')}`\n"
            f"✈️ Airline: {flight_data.get('airline')}\n"
            f"💰 Price: `{flight_data.get('price')} TWD` (Historical Low!)\n"
            f"⏱️ Duration: {flight_data.get('duration_outbound')} with {flight_data.get('stops')} stops\n\n"
            f"[👉 Go to Google Flights]({search_url})"
        )
        return self.send_message(msg)
