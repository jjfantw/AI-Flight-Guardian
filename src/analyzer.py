import pandas as pd
import os
import datetime
import logging

class FlightAnalyzer:
    def __init__(self, records_dir: str = "../records"):
        self.records_dir = records_dir
        os.makedirs(self.records_dir, exist_ok=True)
        
    def process_and_save(self, task_id: str, origin: str, dest: str, dep_date: str, ret_date: str, flights: list[dict]) -> tuple[bool, dict, dict]:
        """
        Process fetched flights, save to CSV, and evaluate if historical low is breached.
        Returns: (is_lowest, cheapest_flight, market_trend_data)
        """
        if not flights:
            return False, {}, self.save_empty_record(task_id, origin, dest, dep_date, ret_date)
            
        csv_path = os.path.join(self.records_dir, f"{task_id}.csv")
        
        # Sort to find the cheapest today
        flights.sort(key=lambda x: x['price'])
        cheapest_today = flights[0]
        
        # Load history
        historical_min_price = float('inf')
        historical_max_price = 0
        avg_price = 0
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if not df.empty and 'price' in df.columns:
                    valid_prices = pd.to_numeric(df['price'], errors='coerce').dropna()
                    if not valid_prices.empty:
                        historical_min_price = valid_prices.min()
                        historical_max_price = valid_prices.max()
                        avg_price = valid_prices.mean()
            except Exception as e:
                logging.error(f"Error reading {csv_path}: {e}")
        
        # Check against history
        is_lowest = False
        if cheapest_today['price'] < historical_min_price and historical_min_price != float('inf'):
            is_lowest = True
            
        # Write to CSV
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        new_row = {
            "timestamp": timestamp,
            "airline": cheapest_today.get("airline"),
            "origin": origin,
            "destination": dest,
            "departure_date": dep_date,
            "return_date": ret_date,
            "stops": cheapest_today.get("stops"),
            "duration_outbound": cheapest_today.get("duration"),
            "price": cheapest_today.get("price"),
            "currency": cheapest_today.get("currency"),
            "is_lowest": is_lowest,
            "search_url": cheapest_today.get("search_url")
        }
        
        new_df = pd.DataFrame([new_row])
        if os.path.exists(csv_path):
            new_df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            # Create new with header
            new_df.to_csv(csv_path, mode='w', header=True, index=False)
            
        trend_data = {
            "today_lowest": cheapest_today['price'],
            "historical_lowest": historical_min_price if historical_min_price != float('inf') else cheapest_today['price'],
            "historical_highest": historical_max_price if historical_max_price > 0 else cheapest_today['price'],
            "historical_avg": avg_price if avg_price > 0 else cheapest_today['price'],
            "historical_lowest_diff": cheapest_today['price'] - historical_min_price if historical_min_price != float('inf') else 0,
            "search_url": cheapest_today.get("search_url")
        }
            
        return is_lowest, new_row, trend_data

    def save_empty_record(self, task_id: str, origin: str, dest: str, dep_date: str, ret_date: str) -> dict:
        """
        Saves a dummy record indicating no flights were found for this timeframe to prevent chart disconnects.
        Returns the historical trend data.
        """
        csv_path = os.path.join(self.records_dir, f"{task_id}.csv")
        
        # Load history
        historical_min_price = float('inf')
        historical_max_price = 0
        avg_price = 0
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if not df.empty and 'price' in df.columns:
                    valid_prices = pd.to_numeric(df['price'], errors='coerce').dropna()
                    if not valid_prices.empty:
                        historical_min_price = valid_prices.min()
                        historical_max_price = valid_prices.max()
                        avg_price = valid_prices.mean()
            except Exception as e:
                logging.error(f"Error reading {csv_path}: {e}")
                
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        new_row = {
            "timestamp": timestamp,
            "airline": "",
            "origin": origin,
            "destination": dest,
            "departure_date": dep_date,
            "return_date": ret_date,
            "stops": "",
            "duration_outbound": "",
            "price": "", # empty to act as null in CSV
            "currency": "TWD",
            "is_lowest": False,
            "search_url": ""
        }
        
        new_df = pd.DataFrame([new_row])
        if os.path.exists(csv_path):
            new_df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            new_df.to_csv(csv_path, mode='w', header=True, index=False)
            
        return {
            "today_lowest": 0,
            "historical_lowest": historical_min_price if historical_min_price != float('inf') else 0,
            "historical_highest": historical_max_price,
            "historical_avg": avg_price,
            "historical_lowest_diff": 0,
            "search_url": ""
        }
