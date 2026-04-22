import logging
import os
from config import get_active_tasks
from notifier import TelegramNotifier
from scraper import FlightScraper
from hub_analyzer import HubRecommender
from analyzer import FlightAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting up AI Flight Guardian - Phase 2 MVP...")
    
    # Handle paths for local vs GitHub Action
    tasks_file = "../tasks.json" if os.path.exists("../tasks.json") else "tasks.json"
    records_dir = "../records" if os.path.exists("../tasks.json") else "records"
    
    active_tasks = get_active_tasks(tasks_file)
    logging.info(f"Loaded {len(active_tasks)} active tasks.")

    if not active_tasks:
        logging.warning("No active tasks found.")
        return

    notifier = TelegramNotifier()
    scraper = FlightScraper()
    hub_recommender = HubRecommender()
    analyzer = FlightAnalyzer(records_dir=records_dir)

    for task in active_tasks:
        origins = task.get("origin", [])
        dests = task.get("destination", [])
        dep_date_start = task.get("departure_date_range", [""])[0]
        arr_date_start = task.get("arrive_period", ["", ""])[0] if task.get("arrive_period") else None
        
        logging.info(f"Processing Task: {task.get('name')}")
        
        # Combine base routes with hub recommendations
        routes_to_check = []
        for o in origins:
            for d in dests:
                routes_to_check.append((o, d))
                
                # Append hub routes
                hubs = hub_recommender.get_hubs(o, d)
                for h in hubs:
                    routes_to_check.append((o, h))  # check origin to hub
                    
        # Check all combined routes
        all_flights = []
        for o, d in routes_to_check:
            logging.info(f"Searching flights: {o} -> {d} on {dep_date_start} arriving {arr_date_start}")
            flights = scraper.search_flights(o, d, dep_date_start, arr_date_start)
            all_flights.extend(flights)
            
        # Analyze and store
        if all_flights:
            # We track the cheapest among the checked routes for MVP
            is_lowest, cheapest_flight, trend_data = analyzer.process_and_save(
                task_id=task.get("id"),
                origin=origins[0], # simplified for MVP
                dest=dests[0], # simplified for MVP
                dep_date=dep_date_start,
                ret_date=arr_date_start,
                flights=all_flights
            )
            
            # Send Daily Summary
            notifier.send_daily_summary(task, trend_data, is_lowest)
            
            # Send Price Drop Alert
            if is_lowest:
                logging.info(f"Price Drop! Triggering alert for {task.get('name')}")
                notifier.send_price_drop_alert(task, cheapest_flight)
        else:
            logging.warning(f"No flights found for task {task.get('name')}")
            trend_data = analyzer.save_empty_record(
                task_id=task.get("id"),
                origin=origins[0],
                dest=dests[0],
                dep_date=dep_date_start,
                ret_date=arr_date_start
            )
            notifier.send_no_flights_summary(task, trend_data)

    logging.info("Phase 2 Execution Completed.")

if __name__ == "__main__":
    main()
