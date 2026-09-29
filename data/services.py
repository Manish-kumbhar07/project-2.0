import pandas as pd
import numpy as np
from data.mumbai_central_line import get_all_stations

def get_services_summary():
    return {
        "total_count": 1810,
        "fast_count": 890,
        "slow_count": 920
    }

def get_hourly_frequency(station_code):
    # Retrieve base data for peak simulation
    stations = get_all_stations()
    station = next((s for s in stations if s['code'] == station_code), None)
    peak = station['peak_services_per_hour'] if station else 15
    
    freq = {}
    for hour in range(24):
        if (8 <= hour <= 11) or (17 <= hour <= 20):
            freq[f"{hour:02d}:00"] = peak
        elif (0 <= hour <= 3):
            freq[f"{hour:02d}:00"] = max(1, int(peak * 0.1))
        else:
            freq[f"{hour:02d}:00"] = max(4, int(peak * 0.4))
            
    return freq

def get_fast_train_stops():
    stations = get_all_stations()
    return [s['code'] for s in stations if s['fast_train_stop']]

def get_service_frequency_matrix():
    stations = get_all_stations()
    station_codes = [s['code'] for s in stations]
    hours = [f"{h:02d}:00" for h in range(24)]
    
    matrix = np.zeros((len(station_codes), 24))
    
    for i, station in enumerate(stations):
        peak = station['peak_services_per_hour']
        for j, hour in enumerate(range(24)):
            if (8 <= hour <= 11) or (17 <= hour <= 20):
                matrix[i, j] = peak
            elif (0 <= hour <= 3):
                matrix[i, j] = max(1, int(peak * 0.1))
            else:
                matrix[i, j] = max(4, int(peak * 0.4))
                
    df = pd.DataFrame(matrix, index=station_codes, columns=hours)
    return df
