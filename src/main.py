import logging
import os
import sys
import traceback
from config import get_active_tasks
from notifier import TelegramNotifier
from scraper import FlightScraper
from hub_analyzer import HubRecommender
from analyzer import FlightAnalyzer
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    logging.info("Starting up AI Flight Guardian - Phase 2 MVP...")
    
    # Debug: Check environment (without leaking secrets)
    secrets_status = {
        "TELEGRAM_BOT_TOKEN": "SET" if os.environ.get("TELEGRAM_BOT_TOKEN") else "MISSING",
        "TELEGRAM_CHAT_ID": "SET" if os.environ.get("TELEGRAM_CHAT_ID") else "MISSING",
        "SERPAPI_KEY": "SET" if os.environ.get("SERPAPI_KEY") else "MISSING"
    }
    logging.info(f"Environment Secrets Check: {secrets_status}")

    try:
        # Handle paths for local vs GitHub Action
        tasks_file = "tasks.json"
        if not os.path.exists(tasks_file):
            if os.path.exists("../tasks.json"):
                tasks_file = "../tasks.json"
            else:
                logging.error("CRITICAL: tasks.json not found in root or parent directory.")
                return

        records_dir = "records"
        if not os.path.exists(records_dir) and os.path.exists("../records"):
            records_dir = "../records"

        active_tasks = get_active_tasks(tasks_file)
        logging.info(f"Loaded {len(active_tasks)} active tasks from {tasks_file}.")

        if not active_tasks:
            logging.warning("No active tasks found or tasks.json is empty.")
            return

        notifier = TelegramNotifier()
        scraper = FlightScraper()
        hub_recommender = HubRecommender()
        analyzer = FlightAnalyzer(records_dir=records_dir)

        for task in active_tasks:
            try:
                task_name = task.get("name", "Unnamed Task")
                logging.info(f"--- Processing Task: {task_name} ---")
                
                origins = task.get("origin", [])
                dests = task.get("destination", [])
                
                if not origins or not dests:
                    logging.warning(f"Skipping task '{task_name}': Missing origin or destination.")
                    continue

                # Prepare date combinations
                base_dep_date = task.get("departure_date")
                base_ret_date = task.get("return_date")
                expand_days = task.get("expand_days", 0)

                # Fallback for old schema
                if not base_dep_date:
                    base_dep_date = task.get("departure_date_range", [""])[0]
                if not base_ret_date:
                    arr_period = task.get("arrive_period", [])
                    base_ret_date = arr_period[0] if arr_period else None

                date_pairs = []
                if base_dep_date:
                    dep_dt = datetime.strptime(base_dep_date, "%Y-%m-%d")
                    ret_dt = datetime.strptime(base_ret_date, "%Y-%m-%d") if base_ret_date else None
                    
                    for d_off in range(-expand_days, expand_days + 1):
                        curr_dep = (dep_dt + timedelta(days=d_off)).strftime("%Y-%m-%d")
                        
                        if ret_dt:
                            for r_off in range(-expand_days, expand_days + 1):
                                curr_ret = (ret_dt + timedelta(days=r_off)).strftime("%Y-%m-%d")
                                if curr_ret >= curr_dep:
                                    date_pairs.append((curr_dep, curr_ret))
                        else:
                            date_pairs.append((curr_dep, None))

                # Combine base routes with hub recommendations
                routes_to_check = []
                for o in origins:
                    for d in dests:
                        routes_to_check.append((o, d))
                        hubs = hub_recommender.get_hubs(o, d)
                        for h in hubs:
                            routes_to_check.append((o, h))
                            
                # Check all combinations
                all_flights = []
                for o, d in routes_to_check:
                    for dep, ret in date_pairs:
                        logging.info(f"Searching flights: {o} -> {d} on {dep} (Return: {ret})")
                        flights = scraper.search_flights(o, d, dep, ret)
                        all_flights.extend(flights)
                    
                # Analyze and store
                if all_flights:
                    is_lowest, cheapest_flight, trend_data = analyzer.process_and_save(
                        task_id=task.get("id"),
                        origin=origins[0],
                        dest=dests[0],
                        dep_date=base_dep_date,
                        ret_date=base_ret_date,
                        flights=all_flights
                    )
                    
                    # Send Daily Summary
                    logging.info(f"Sending daily summary for {task_name}...")
                    notifier.send_daily_summary(task, trend_data, is_lowest)
                    
                    # Send Price Drop Alert
                    if is_lowest:
                        logging.info(f"Price Drop! Triggering alert for {task_name}")
                        notifier.send_price_drop_alert(task, cheapest_flight)
                else:
                    logging.warning(f"No flights found for task {task_name}")
                    trend_data = analyzer.save_empty_record(
                        task_id=task.get("id"),
                        origin=origins[0],
                        dest=dests[0],
                        dep_date=base_dep_date,
                        ret_date=base_ret_date
                    )
                    notifier.send_no_flights_summary(task, trend_data)
                    
            except Exception as task_error:
                logging.error(f"Error processing task {task.get('name')}: {task_error}")
                logging.error(traceback.format_exc())

    except Exception as e:
        logging.error(f"FATAL ERROR during execution: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)

    logging.info("Phase 2 Execution Completed Successfully.")

if __name__ == "__main__":
    main()
