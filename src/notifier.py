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
        )
        
        # Add quick look at the best flight if available
        best_flight = trend_data.get("best_flight_meta") # We might need to pass this in
        if best_flight:
            msg += "\n\n✈️ *Latest Best Flight Detail:*\n"
            msg += f"🛫 去程: {best_flight.get('airline')} ({best_flight.get('departure_time', 'N/A')})\n"
            if best_flight.get("return_airline"):
                msg += f"🛬 回程: {best_flight.get('return_airline')} ({best_flight.get('return_departure_time', 'N/A')})\n"
            if best_flight.get("outbound_layovers") or best_flight.get("return_layovers"):
                msg += f"🔄 轉機: {best_flight.get('outbound_layovers')} / {best_flight.get('return_layovers')}\n"

        msg += f"\n\n[👉 Go to Google Flights]({search_url})"
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
            f"**Task**: `{task.get('name')}`\n\n"
            f"💰 Price: `{flight_data.get('price')} TWD` (Historical Low!)\n"
            f"✈️ *Flight Details:*\n"
            f"🛫 Outbound: {flight_data.get('airline')} | {flight_data.get('departure_time')}\n"
        )
        
        if flight_data.get("return_airline"):
            msg += f"🛬 Return: {flight_data.get('return_airline')} | {flight_data.get('return_departure_time')}\n"
            
        if flight_data.get("outbound_layovers") or flight_data.get("return_layovers"):
             msg += f"🔄 Layovers: {flight_data.get('outbound_layovers')} / {flight_data.get('return_layovers')}\n"
             
        msg += f"⏱️ Total Duration: {flight_data.get('duration')}\n"
        
        if flight_data.get("booking_token"):
            msg += f"🎫 Booking Token: `{flight_data.get('booking_token')[:10]}...`\n"
            
        msg += f"\n[👉 Book on Google Flights]({search_url})"
        return self.send_message(msg)
