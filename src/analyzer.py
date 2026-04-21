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
            return False, {}, {}
            
        csv_path = os.path.join(self.records_dir, f"{task_id}.csv")
        
        # Sort to find the cheapest today
        flights.sort(key=lambda x: x['price'])
        cheapest_today = flights[0]
        
        # Load history
        historical_min_price = float('inf')
        avg_price = 0
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if not df.empty and 'price' in df.columns:
                    historical_min_price = df['price'].min()
                    avg_price = df['price'].mean()
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
            "is_lowest": is_lowest
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
            "historical_avg": avg_price if avg_price > 0 else cheapest_today['price'],
            "historical_lowest_diff": cheapest_today['price'] - historical_min_price if historical_min_price != float('inf') else 0
        }
            
        return is_lowest, new_row, trend_data
