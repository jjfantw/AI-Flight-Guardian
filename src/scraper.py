import os
import requests
import logging
import random

class FlightScraper:
    def __init__(self, api_key: str = None):
        """
        Base tool to fetch flight data. 
        For MVP, we support SerpApi (Google Flights). If no API key is provided,
        it uses mock data to ensure CI/CD and pipeline stability without incurring costs.
        """
        self.api_key = api_key or os.environ.get("SERPAPI_KEY")
        
    def search_flights(self, origin: str, destination: str, departure_date: str, return_date: str = None) -> list[dict]:
        """
        Searches flights between two airports. Returns a list of parsed flight dictionaries.
        """
        if not self.api_key:
            logging.info(f"[MOCK DATA] Searching flights {origin} -> {destination} on {departure_date}")
            return self._get_mock_data(origin, destination, departure_date, return_date)
            
        # Actual SerpApi implementation
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "currency": "TWD",
            "hl": "zh-tw",
            "api_key": self.api_key
        }
        
        if return_date:
            params["return_date"] = return_date

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return self._parse_serpapi_response(data)
        except Exception as e:
            logging.error(f"Failed to fetch from SerpApi: {e}")
            return []

    def _parse_serpapi_response(self, data: dict) -> list[dict]:
        results = []
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        
        # Capture the search result URL from metadata
        search_url = data.get("google_flights_url", "https://www.google.com/travel/flights")
        
        for flight in best_flights + other_flights:
            try:
                price = flight.get("price", 0)
                airline_info = flight.get("flights", [{}])[0]
                airline = airline_info.get("airline", "Unknown")
                stops = flight.get("layovers", [])
                num_stops = len(stops) if stops else 0
                total_duration = flight.get("total_duration", 0) # minutes
                
                hours = total_duration // 60
                mins = total_duration % 60
                duration_str = f"{hours}h{mins}m"
                
                results.append({
                    "airline": airline,
                    "price": price,
                    "stops": num_stops,
                    "duration": duration_str,
                    "currency": "TWD",
                    "search_url": search_url
                })
            except Exception as e:
                logging.warning(f"Error parsing a flight result: {e}")
                continue
        return results

    def _get_mock_data(self, origin, destination, dep_date, ret_date) -> list[dict]:
        # Returns semi-realistic mock data
        # Using Google Search query format as it's more reliable for pre-filling criteria than direct Flights URL without tfs
        mock_url = f"https://www.google.com/search?q=flights+from+{origin}+to+{destination}+on+{dep_date}"
        if ret_date:
            mock_url += f"+to+{ret_date}"
            
        return [
            {
                "airline": random.choice(["EK (Emirates)", "BR (EVA Air)", "CI (China Airlines)", "TK (Turkish Airlines)"]),
                "price": random.randint(22000, 45000),
                "stops": random.randint(0, 2),
                "duration": f"{random.randint(12, 20)}h{random.randint(0, 59)}m",
                "currency": "TWD",
                "search_url": mock_url
            } for _ in range(3)
        ]
