import re
from typing import Dict, Any

def extract_entities_and_priority(text: str) -> Dict[str, Any]:
    """
    Parses raw report text to extract hazard classification, 
    estimated victim counts, and severity keywords for Talegaon Dabhade.
    """
    text_lower = text.lower()
    
    # Keyword-based hazard classification
    hazard_type = "General Emergency"
    if any(w in text_lower for w in ["flood", "water", "submerged", "river", "rain"]):
        hazard_type = "Flood / Water Logging"
    elif any(w in text_lower for w in ["accident", "collision", "highway", "crash", "nh48"]):
        hazard_type = "Highway Road Blockade / Crash"
    elif any(w in text_lower for w in ["building", "collapse", "structure", "wall", "landslide"]):
        hazard_type = "Structural Collapse / Landslide"
    elif any(w in text_lower for w in ["fire", "smoke", "short circuit", "blaze"]):
        hazard_type = "Fire / Electrical Hazard"

    # Heuristic victim count extraction using regex looking for numbers near people-related terms
    victim_count = 2 # default baseline
    people_match = re.search(r'(\d+)\s*(people|persons|victims|injured|trapped|kids|children)', text_lower)
    if people_match:
        victim_count = int(people_match.group(1))
    elif any(w in text_lower for w in ["many", "dozens", "crowd", "severe", "mass"]):
        victim_count = 10

    return {
        "hazard_type": hazard_type,
        "estimated_victims": victim_count
    }