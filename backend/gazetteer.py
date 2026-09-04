from typing import Optional, Dict

# Offline lookup directory for Talegaon Dabhade landmarks
TALEGAON_GAZETTEER: Dict[str, Dict[str, float]] = {
    "talegaon station": {"lat": 18.7305, "lng": 73.6812},
    "railway station": {"lat": 18.7305, "lng": 73.6812},
    "indrayani river": {"lat": 18.7450, "lng": 73.6600},
    "nh48": {"lat": 18.7200, "lng": 73.6900},
    "old pune mumbai highway": {"lat": 18.7200, "lng": 73.6900},
    "talegaon midc": {"lat": 18.7150, "lng": 73.6550},
    "general hospital": {"lat": 18.7330, "lng": 73.6780}
}

def resolve_location_from_text(text: str) -> Optional[Dict[str, float]]:
    """
    Scans raw incident text for known Talegaon landmarks 
    and returns fallback GPS coordinates during connectivity drops.
    """
    text_lower = text.lower()
    for landmark, coords in TALEGAON_GAZETTEER.items():
        if landmark in text_lower:
            return coords
    return None