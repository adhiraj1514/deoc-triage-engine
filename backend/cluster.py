import os
import sys
import math
from typing import List, Dict, Any

# Ensure backend directory is in sys.path so imports work both locally and in cloud deployment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gazetteer import resolve_location_from_text
from nlp_ner import extract_entities_and_priority

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates accurate surface distance in kilometers between two GPS coordinates
    using the equirectangular approximation (accurate for local <50 km scales).
    """
    # Mean radius of Earth in km
    R = 6371.0
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    
    x = (lon2_rad - lon1_rad) * math.cos((lat1_rad + lat2_rad) / 2.0)
    y = lat2_rad - lat1_rad
    return math.sqrt(x**2 + y**2) * R

def cluster_disaster_reports(reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ingests raw disaster reports, resolves missing coordinates via offline gazetteer,
    runs NLP entity extraction, and groups incidents into 1km spatial clusters.
    """
    if not reports:
        return []

    processed_reports = []

    # Step 1: Pre-process reports, resolve missing coordinates, extract NLP metadata
    for r in reports:
        current_lat = r.get("lat")
        current_lng = r.get("lng")
        text = r.get("text", "")
        
        # Resolve coordinates via offline gazetteer if missing or zero
        if current_lat is None or current_lng is None or (current_lat == 0.0 and current_lng == 0.0):
            resolved = resolve_location_from_text(text)
            if resolved:
                current_lat = resolved["lat"]
                current_lng = resolved["lng"]
            else:
                # Default fallback center for Talegaon Dabhade station area
                current_lat = 18.7305
                current_lng = 73.6812

        # Extract NLP hazard classification and baseline victims
        nlp_data = extract_entities_and_priority(text)

        processed_reports.append({
            "id": r.get("id"),
            "text": text,
            "lat": current_lat,
            "lng": current_lng,
            "timestamp": r.get("timestamp"),
            "hazard_type": nlp_data.get("hazard_type", "General Emergency"),
            "estimated_victims": nlp_data.get("estimated_victims", 0)
        })

    clusters = []
    processed_ids = set()

    # Step 2: Spatial Aggregation (1km Radius)
    for report in processed_reports:
        if report["id"] in processed_ids:
            continue

        current_cluster = [report]
        processed_ids.add(report["id"])

        for other in processed_reports:
            if other["id"] not in processed_ids:
                dist = calculate_distance(report["lat"], report["lng"], other["lat"], other["lng"])
                if dist <= 1.0:  # Within 1 kilometer radius
                    current_cluster.append(other)
                    processed_ids.add(other["id"])

        total_reports = len(current_cluster)
        total_victims = sum(item["estimated_victims"] for item in current_cluster)
        
        # Determine centroid coordinates for accurate pin placement
        avg_lat = sum(item["lat"] for item in current_cluster) / total_reports
        avg_lng = sum(item["lng"] for item in current_cluster) / total_reports

        # Determine dominant hazard type for the cluster
        hazard_types = [item["hazard_type"] for item in current_cluster]
        dominant_hazard = max(set(hazard_types), key=hazard_types.count)

        # Dynamic Priority Classification (Cognitive Overload Shield logic)
        priority = "P3 - Moderate"
        if total_reports >= 4 or total_victims >= 15:
            priority = "P1 - CRITICAL"
        elif total_reports >= 2 or total_victims >= 6:
            priority = "P2 - High"

        clusters.append({
            "cluster_id": f"cluster_{report['id']}",
            "latitude": round(avg_lat, 6),
            "longitude": round(avg_lng, 6),
            "total_reports": total_reports,
            "estimated_victims": total_victims,
            "priority_level": priority,
            "hazard_type": dominant_hazard,
            "sample_messages": [item["text"] for item in current_cluster[:3]]
        })

    return clusters