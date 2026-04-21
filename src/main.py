import logging
from config import get_active_tasks
from notifier import TelegramNotifier

def main():
    logging.info("Starting Phase 1 Mock Verification...")
    
    # 1. Load active tasks
    active_tasks = get_active_tasks("../tasks.json") if __name__ != "__main__" else get_active_tasks("tasks.json")
    logging.info(f"Loaded {len(active_tasks)} active tasks.")

    if not active_tasks:
        logging.warning("No active tasks found in tasks.json.")
        return

    # 2. Format a mock test message based on the tasks retrieved.
    test_task = active_tasks[0]
    
    mock_message_lines = [
        "✈️ *AI Flight Guardian - Phase 1 verification*",
        f"✅ Loaded Task config for: `{test_task.get('name')}`",
        f"📅 Date Range: `{test_task.get('departure_date_range')[0]}` to `{test_task.get('departure_date_range')[1]}`",
        f"🗺️ Origins: `{', '.join(test_task.get('origin', []))}`",
        f"🗺️ Destinations: `{', '.join(test_task.get('destination', []))}`",
        "",
        "If you see this message, the basic GitHub infrastructure, configuration reading, and notification modules are successfully connected!"
    ]
    
    test_msg = "\n".join(mock_message_lines)

    # 3. Initialize notifier and send message
    notifier = TelegramNotifier()
    success = notifier.send_message(test_msg)
    
    if success:
        logging.info("Phase 1 verification run finished successfully.")
    else:
        logging.error("Phase 1 verification run encountered errors sending notifications.")

if __name__ == "__main__":
    main()
