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
            "return_airline": cheapest_today.get("return_airline"),
            "origin": origin,
            "destination": dest,
            "departure_date": dep_date,
            "return_date": ret_date,
            "departure_time": cheapest_today.get("departure_time"),
            "arrival_time": cheapest_today.get("arrival_time"),
            "return_departure_time": cheapest_today.get("return_departure_time"),
            "return_arrival_time": cheapest_today.get("return_arrival_time"),
            "outbound_layovers": cheapest_today.get("outbound_layovers"),
            "return_layovers": cheapest_today.get("return_layovers"),
            "stops": cheapest_today.get("stops"),
            "duration": cheapest_today.get("duration"),
            "price": cheapest_today.get("price"),
            "currency": cheapest_today.get("currency"),
            "is_lowest": is_lowest,
            "search_url": cheapest_today.get("search_url"),
            "booking_token": cheapest_today.get("booking_token")
        }
        
        new_df = pd.DataFrame([new_row])
        if os.path.exists(csv_path):
            try:
                # Attempt to read existing data
                try:
                    existing_df = pd.read_csv(csv_path)
                except Exception:
                    # Fallback if file is corrupted due to mismatched columns
                    logging.warning(f"CSV {csv_path} seems corrupted. Attempting recovery...")
                    existing_df = pd.read_csv(csv_path, on_bad_lines='skip')
                
                if not all(col in existing_df.columns for col in new_row.keys()):
                    logging.info(f"Migrating CSV schema for {csv_path}...")
                    # Ensure all new columns exist in existing_df
                    for col in new_row.keys():
                        if col not in existing_df.columns:
                            existing_df[col] = ""
                    
                    # Also handle columns that might have been renamed (e.g. duration_outbound -> duration)
                    if 'duration_outbound' in existing_df.columns and 'duration' in existing_df.columns:
                         existing_df['duration'] = existing_df['duration'].fillna(existing_df['duration_outbound'])
                    
                    # Reorder to match new schema
                    existing_df = existing_df[list(new_row.keys())]
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    combined_df.to_csv(csv_path, index=False)
                else:
                    new_df.to_csv(csv_path, mode='a', header=False, index=False)
            except Exception as e:
                logging.error(f"Error migrating/appending to {csv_path}: {e}")
                new_df.to_csv(csv_path, mode='w', header=True, index=False)
        else:
            # Create new with header
            new_df.to_csv(csv_path, mode='w', header=True, index=False)
            
        trend_data = {
            "today_lowest": cheapest_today['price'],
            "historical_lowest": historical_min_price if historical_min_price != float('inf') else cheapest_today['price'],
            "historical_highest": historical_max_price if historical_max_price > 0 else cheapest_today['price'],
            "historical_avg": avg_price if avg_price > 0 else cheapest_today['price'],
            "historical_lowest_diff": cheapest_today['price'] - historical_min_price if historical_min_price != float('inf') else 0,
            "search_url": cheapest_today.get("search_url"),
            "best_flight_meta": new_row
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
            "return_airline": "",
            "origin": origin,
            "destination": dest,
            "departure_date": dep_date,
            "return_date": ret_date,
            "departure_time": "",
            "arrival_time": "",
            "return_departure_time": "",
            "return_arrival_time": "",
            "outbound_layovers": "",
            "return_layovers": "",
            "stops": "",
            "duration": "",
            "price": "", # empty to act as null in CSV
            "currency": "TWD",
            "is_lowest": False,
            "search_url": "",
            "booking_token": ""
        }
        
        new_df = pd.DataFrame([new_row])
        if os.path.exists(csv_path):
            try:
                existing_df = pd.read_csv(csv_path)
                if not all(col in existing_df.columns for col in new_row.keys()):
                    logging.info(f"Migrating CSV schema for {csv_path} (Empty Record)...")
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    combined_df.to_csv(csv_path, index=False)
                else:
                    new_df.to_csv(csv_path, mode='a', header=False, index=False)
            except Exception as e:
                logging.error(f"Error migrating/appending empty record to {csv_path}: {e}")
                new_df.to_csv(csv_path, mode='w', header=True, index=False)
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
