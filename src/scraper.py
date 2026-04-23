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
        
        # Determine the target destination to split outbound/return
        # The request params usually have arrival_id
        target_dest = data.get("search_parameters", {}).get("arrival_id")

        for flight in best_flights + other_flights:
            try:
                price = flight.get("price", 0)
                segments = flight.get("flights", [])
                if not segments:
                    continue
                
                # Split segments into outbound and return
                outbound_segments = []
                return_segments = []
                
                reached_dest = False
                for seg in segments:
                    if not reached_dest:
                        outbound_segments.append(seg)
                        if seg.get("arrival_airport", {}).get("id") == target_dest:
                            reached_dest = True
                    else:
                        return_segments.append(seg)

                # Basic Info
                airline = outbound_segments[0].get("airline", "Unknown")
                ret_airline = return_segments[0].get("airline", "Unknown") if return_segments else ""
                
                # Times
                dep_time = outbound_segments[0].get("departure_airport", {}).get("time", "")
                arr_time = outbound_segments[-1].get("arrival_airport", {}).get("time", "")
                
                ret_dep_time = return_segments[0].get("departure_airport", {}).get("time", "") if return_segments else ""
                ret_arr_time = return_segments[-1].get("arrival_airport", {}).get("time", "") if return_segments else ""

                # Layovers
                outbound_layovers = [l.get("id") for l in flight.get("layovers", []) if any(seg.get("arrival_airport", {}).get("id") == l.get("id") for seg in outbound_segments)]
                return_layovers = [l.get("id") for l in flight.get("layovers", []) if any(seg.get("arrival_airport", {}).get("id") == l.get("id") for seg in return_segments)]
                
                # Booking info
                booking_token = flight.get("booking_token", "")
                
                total_duration = flight.get("total_duration", 0)
                duration_str = f"{total_duration // 60}h{total_duration % 60}m"
                
                results.append({
                    "airline": airline,
                    "return_airline": ret_airline,
                    "price": price,
                    "stops": len(outbound_layovers) + len(return_layovers),
                    "outbound_layovers": ",".join(outbound_layovers),
                    "return_layovers": ",".join(return_layovers),
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "return_departure_time": ret_dep_time,
                    "return_arrival_time": ret_arr_time,
                    "duration": duration_str,
                    "currency": "TWD",
                    "search_url": search_url,
                    "booking_token": booking_token
                })
            except Exception as e:
                logging.warning(f"Error parsing a flight result: {e}")
                continue
        return results

    def _get_mock_data(self, origin, destination, dep_date, ret_date) -> list[dict]:
        # Returns semi-realistic mock data
        mock_url = f"https://www.google.com/search?q=flights+from+{origin}+to+{destination}+on+{dep_date}"
        if ret_date:
            mock_url += f"+to+{ret_date}"
            
        results = []
        for _ in range(3):
            airline = random.choice(["EK (Emirates)", "BR (EVA Air)", "CI (China Airlines)", "TK (Turkish Airlines)"])
            ret_airline = random.choice(["EK (Emirates)", "BR (EVA Air)", "CI (China Airlines)"]) if ret_date else ""
            
            results.append({
                "airline": airline,
                "return_airline": ret_airline,
                "price": random.randint(22000, 45000),
                "stops": random.randint(0, 2),
                "outbound_layovers": "HKG" if random.random() > 0.5 else "",
                "return_layovers": "HKG" if (ret_date and random.random() > 0.5) else "",
                "departure_time": f"{dep_date} 08:{random.randint(10,59)}",
                "arrival_time": f"{dep_date} 21:{random.randint(10,59)}",
                "return_departure_time": f"{ret_date} 10:{random.randint(10,59)}" if ret_date else "",
                "return_arrival_time": f"{ret_date} 23:{random.randint(10,59)}" if ret_date else "",
                "duration": f"{random.randint(12, 20)}h{random.randint(0, 59)}m",
                "currency": "TWD",
                "search_url": mock_url,
                "booking_token": "mock_token_" + str(random.randint(1000, 9999))
            })
        return results
