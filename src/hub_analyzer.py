class HubRecommender:
    def __init__(self):
        """
        Provides dynamic hub routing recommendations based on the region.
        For MVP, we use static mappings (which solves 80% of the use case without API costs).
        """
        # Mapping origin airports to sensible hubs based on destination category
        self.hub_mapping = {
            "TPE_TO_EU": ["DXB", "IST", "BKK"],
            "TPE_TO_US": ["NRT", "HND", "SFO", "LAX"]
        }
        
        # Categorize known destinations
        self.eu_airports = {"CDG", "AMS", "LHR", "FRA", "MUC", "MXP", "MAD", "BCN"}
        self.us_airports = {"JFK", "LAX", "SFO", "ORD", "EWR", "SEA"}

    def get_hubs(self, origin: str, destination: str) -> list[str]:
        """
        Returns a list of reasonable hub airports to check based on the flight's endpoints.
        """
        hubs = []
        if origin in ["TPE", "KIX"]: # Common East Asian departure nodes
            if destination in self.eu_airports:
                hubs.extend(self.hub_mapping["TPE_TO_EU"])
            elif destination in self.us_airports:
                hubs.extend(self.hub_mapping["TPE_TO_US"])
                
        # Deduplicate and ensure we aren't suggesting the destination as a hub
        hubs = list(set([h for h in hubs if h != destination]))
        return hubs
