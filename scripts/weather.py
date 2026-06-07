import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
# Mapping of IPL venues/cities to coordinates (Latitude, Longitude)
VENUE_COORDINATES = {
    # Hyderabad
    "rajiv gandhi international stadium, uppal": (17.4062, 78.5505),
    "rajiv gandhi international stadium": (17.4062, 78.5505),
    "hyderabad": (17.3850, 78.4867),
    
    # Bengaluru
    "m chinnaswamy stadium": (12.9788, 77.5997),
    "m.chinnaswamy stadium": (12.9788, 77.5997),
    "bangalore": (12.9716, 77.5946),
    
    # Mumbai
    "wankhede stadium": (18.9389, 72.8258),
    "brabourne stadium": (18.9317, 72.8244),
    "dr dy patil sports academy": (19.0313, 73.0182),
    "dr. dy patil sports academy": (19.0313, 73.0182),
    "mumbai": (19.0760, 72.8777),
    
    # Kolkata
    "eden gardens": (22.5646, 88.3433),
    "kolkata": (22.5726, 88.3639),
    
    # Delhi
    "arun jaitley stadium": (28.6376, 77.2433),
    "feroz shah kotla": (28.6376, 77.2433),
    "feroz shah kotla ground": (28.6376, 77.2433),
    "delhi": (28.7041, 77.1025),
    
    # Chennai
    "ma chidambaram stadium, chepauk": (13.0628, 80.2793),
    "ma chidambaram stadium": (13.0628, 80.2793),
    "ma chidambaram stadium, chepauk, chennai": (13.0628, 80.2793),
    "chennai": (13.0827, 80.2707),
    
    # Mohali / Chandigarh
    "punjab cricket association is bindra stadium, mohali": (30.6909, 76.7374),
    "punjab cricket association is bindra stadium": (30.6909, 76.7374),
    "punjab cricket association stadium, mohali": (30.6909, 76.7374),
    "mohali": (30.6970, 76.7214),
    "chandigarh": (30.7333, 76.7794),
    
    # Jaipur
    "sawai mansingh stadium": (26.8940, 75.8031),
    "jaipur": (26.9124, 75.7873),
    
    # Ahmedabad
    "narendra modi stadium": (23.0916, 72.5975),
    "sardar patel stadium, motera": (23.0916, 72.5975),
    "ahmedabad": (23.0225, 72.5714),
    
    # Pune
    "maharashtra cricket association stadium": (18.6744, 73.7064),
    "subrata roy sahara stadium": (18.6744, 73.7064),
    "pune": (18.5204, 73.8567),
    
    # Visakhapatnam
    "dr. y.s. rajasekhara reddy aca-vdca cricket stadium": (17.7972, 83.3506),
    "dr y.s. rajasekhara reddy aca-vdca cricket stadium": (17.7972, 83.3506),
    "visakhapatnam": (17.6868, 83.2185),
    
    # Lucknow
    "bharat ratna shri atal bihari vajpayee ekana cricket stadium, lucknow": (26.8014, 80.9889),
    "bharat ratna shri atal bihari vajpayee ekana cricket stadium": (26.8014, 80.9889),
    "ekana cricket stadium": (26.8014, 80.9889),
    "lucknow": (26.8467, 80.9462),
    
    # Dharamshala
    "himachal pradesh cricket association stadium, dharamshala": (32.1977, 76.3256),
    "himachal pradesh cricket association stadium": (32.1977, 76.3256),
    "dharamshala": (32.2190, 76.3234),
    
    # Indore
    "holkar cricket stadium": (22.7244, 75.8789),
    "indore": (22.7196, 75.8577),
    
    # Ranchi
    "jsca international stadium complex": (23.3106, 85.2758),
    "ranchi": (23.3441, 85.3096),
    
    # Rajkot
    "saurashtra cricket association stadium": (22.3619, 70.7811),
    "rajkot": (22.3039, 70.8022),
    
    # UAE
    "dubai international cricket stadium": (25.0481, 55.2194),
    "sharjah cricket stadium": (25.3308, 55.4211),
    "sheikh zayed stadium": (24.3986, 54.5481),
    "zayed cricket stadium, abu dhabi": (24.3986, 54.5481),
    "abu dhabi": (24.4539, 54.3773),
    "dubai": (25.2048, 55.2708),
    "sharjah": (25.3463, 55.4209),
    
    # South Africa
    "supersport park": (-25.8602, 28.1952),
    "new wanderers stadium": (-26.1325, 28.0583),
    "st george's park": (-33.9667, 25.6000),
    "kingsmead": (-29.8486, 31.0286),
    "newlands": (-33.9731, 18.4681),
    "de beers diamond oval": (-28.7383, 24.7828),
    "buffalo park": (-33.0039, 27.9189),
    "outsurance oval": (-29.1167, 26.2167),
    "centurion": (-25.8587, 28.1856),
    "johannesburg": (-26.2041, 28.0473),
    "durban": (-29.8587, 31.0218),
    "cape town": (-33.9249, 18.4241),
    "port elizabeth": (-33.9608, 25.6022),
    
    # Others
    "barabati stadium": (20.4808, 85.8789),
    "cuttack": (20.4625, 85.8830),
    "green park": (26.4828, 80.3475),
    "kanpur": (26.4499, 80.3319),
    "shaheed veer narayan singh international stadium": (21.1969, 81.7781),
    "raipur": (21.2514, 81.6296),
}
# General climate fallback data by region/city and month of the year (mostly March, April, May, October, November)
# Format: month_num: (avg_temp_c, avg_humidity_pct)
CLIMATE_FALLBACKS = {
    # Default/Generic IPL season (Spring/Summer India)
    "default": {
        3: (31.0, 45.0),
        4: (35.0, 40.0),
        5: (38.0, 45.0),
        9: (32.0, 75.0),
        10: (30.0, 65.0),
        11: (28.0, 55.0),
        "other": (28.0, 50.0)
    },
    # Coastal/Humid cities (Mumbai, Chennai, Kolkata, Visakhapatnam, Durban)
    "humid": {
        3: (32.0, 70.0),
        4: (33.0, 75.0),
        5: (34.0, 78.0),
        9: (31.0, 82.0),
        10: (31.0, 78.0),
        11: (30.0, 72.0),
        "other": (29.0, 75.0)
    },
    # Inland/Dry/Hot cities (Delhi, Ahmedabad, Hyderabad, Jaipur, Nagpur)
    "dry": {
        3: (31.0, 35.0),
        4: (37.0, 25.0),
        5: (41.0, 25.0),
        9: (33.0, 60.0),
        10: (32.0, 45.0),
        11: (28.0, 40.0),
        "other": (26.0, 40.0)
    },
    # UAE (Dubai, Abu Dhabi, Sharjah)
    "uae": {
        3: (28.0, 55.0),
        4: (33.0, 50.0),
        5: (38.0, 45.0),
        9: (39.0, 60.0),
        10: (35.0, 60.0),
        11: (31.0, 60.0),
        "other": (25.0, 55.0)
    },
    # South Africa (Centurion, Johannesburg) - Note IPL 2009 was April-May (Autumn there)
    "sa_highveld": {
        3: (24.0, 55.0),
        4: (21.0, 50.0),
        5: (18.0, 45.0),
        "other": (20.0, 50.0)
    }
}
# Map stadium names to climate categories for fallback
STADIUM_CLIMATE_MAP = {
    # Humid / Coastal
    "wankhede stadium": "humid",
    "brabourne stadium": "humid",
    "dr dy patil sports academy": "humid",
    "dr. dy patil sports academy": "humid",
    "mumbai": "humid",
    "ma chidambaram stadium, chepauk": "humid",
    "ma chidambaram stadium": "humid",
    "ma chidambaram stadium, chepauk, chennai": "humid",
    "chennai": "humid",
    "eden gardens": "humid",
    "kolkata": "humid",
    "dr. y.s. rajasekhara reddy aca-vdca cricket stadium": "humid",
    "visakhapatnam": "humid",
    "barabati stadium": "humid",
    "cuttack": "humid",
    "kingsmead": "humid",
    "durban": "humid",
    "newlands": "humid",
    "cape town": "humid",
    "st george's park": "humid",
    "port elizabeth": "humid",
    "buffalo park": "humid",
    # Dry / Hot
    "arun jaitley stadium": "dry",
    "feroz shah kotla": "dry",
    "delhi": "dry",
    "sawai mansingh stadium": "dry",
    "jaipur": "dry",
    "narendra modi stadium": "dry",
    "sardar patel stadium, motera": "dry",
    "ahmedabad": "dry",
    "rajiv gandhi international stadium, uppal": "dry",
    "rajiv gandhi international stadium": "dry",
    "hyderabad": "dry",
    "bharat ratna shri atal bihari vajpayee ekana cricket stadium, lucknow": "dry",
    "ekana cricket stadium": "dry",
    "lucknow": "dry",
    "green park": "dry",
    "kanpur": "dry",
    # UAE
    "dubai international cricket stadium": "uae",
    "sharjah cricket stadium": "uae",
    "sheikh zayed stadium": "uae",
    "zayed cricket stadium, abu dhabi": "uae",
    "dubai": "uae",
    "sharjah": "uae",
    "abu dhabi": "uae",
    # South Africa Inland
    "supersport park": "sa_highveld",
    "new wanderers stadium": "sa_highveld",
    "centurion": "sa_highveld",
    "johannesburg": "sa_highveld",
}
# Pitch classifications
PITCH_TYPES = {
    "m chinnaswamy stadium": "Flat / Batting Friendly",
    "m.chinnaswamy stadium": "Flat / Batting Friendly",
    "bangalore": "Flat / Batting Friendly",
    "holkar cricket stadium": "Flat / Batting Friendly",
    "indore": "Flat / Batting Friendly",
    "sharjah cricket stadium": "Flat / Batting Friendly",
    "sharjah": "Flat / Batting Friendly",
    
    "ma chidambaram stadium, chepauk": "Slow / Spin Friendly",
    "ma chidambaram stadium": "Slow / Spin Friendly",
    "ma chidambaram stadium, chepauk, chennai": "Slow / Spin Friendly",
    "chennai": "Slow / Spin Friendly",
    "bharat ratna shri atal bihari vajpayee ekana cricket stadium, lucknow": "Slow / Spin Friendly",
    "ekana cricket stadium": "Slow / Spin Friendly",
    "lucknow": "Slow / Spin Friendly",
    "jsca international stadium complex": "Slow / Spin Friendly",
    "ranchi": "Slow / Spin Friendly",
    
    "himachal pradesh cricket association stadium, dharamshala": "Pace / Swing Friendly",
    "himachal pradesh cricket association stadium": "Pace / Swing Friendly",
    "dharamshala": "Pace / Swing Friendly",
    "punjab cricket association is bindra stadium, mohali": "Pace / Bounce Friendly",
    "punjab cricket association stadium, mohali": "Pace / Bounce Friendly",
    "mohali": "Pace / Bounce Friendly",
    
    "wankhede stadium": "Flat / Pace Friendly",
    "brabourne stadium": "Flat / Pace Friendly",
    "dr dy patil sports academy": "Flat / Pace Friendly",
    "dr. dy patil sports academy": "Flat / Pace Friendly",
    "mumbai": "Flat / Pace Friendly",
    "eden gardens": "Flat / Pace Friendly",
    "kolkata": "Flat / Pace Friendly",
}
class WeatherPitchLookup:
    def __init__(self, cache_dir="data/processed"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "weather_cache.json")
        self.cache = {}
        self.load_cache()
    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load weather cache: {e}")
        else:
            os.makedirs(self.cache_dir, exist_ok=True)
            self.cache = {}
    def save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save weather cache: {e}")
    def get_pitch_type(self, venue):
        if not venue:
            return "Balanced"
        v_lower = venue.lower().strip()
        
        # Check direct matches
        for k, v in PITCH_TYPES.items():
            if k in v_lower:
                return v
        
        # Balance defaults
        if "spin" in v_lower or "slow" in v_lower:
            return "Slow / Spin Friendly"
        if "green" in v_lower or "grass" in v_lower:
            return "Pace / Swing Friendly"
        if "flat" in v_lower or "bat" in v_lower:
            return "Flat / Batting Friendly"
            
        return "Balanced"
    def get_fallback_weather(self, venue, date_obj):
        month = date_obj.month
        v_lower = venue.lower().strip() if venue else ""
        
        category = "default"
        for k, cat in STADIUM_CLIMATE_MAP.items():
            if k in v_lower:
                category = cat
                break
                
        month_data = CLIMATE_FALLBACKS.get(category, CLIMATE_FALLBACKS["default"])
        temp, humidity = month_data.get(month, month_data.get("other", (30.0, 50.0)))
        return temp, humidity
    def get_weather(self, venue, date_str, use_api=True):
        # Normalize date
        try:
            # Handle formats like YYYY-MM-DD or YYYY/MM/DD
            date_str_norm = date_str.replace("/", "-")
            date_obj = datetime.strptime(date_str_norm, "%Y-%m-%d")
            api_date_str = date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
            return 30.0, 50.0 # Default fallback
            
        # Get coordinates
        v_lower = venue.lower().strip() if venue else ""
        coords = None
        for k, lat_lon in VENUE_COORDINATES.items():
            if k in v_lower:
                coords = lat_lon
                break
                
        if not coords:
            # Fall back to monthly climatology if venue unknown
            return self.get_fallback_weather(venue, date_obj)
        # Check Cache
        cache_key = f"{coords[0]:.4f}_{coords[1]:.4f}_{api_date_str}"
        if cache_key in self.cache:
            return self.cache[cache_key]["temp"], self.cache[cache_key]["humidity"]
        if not use_api:
            return self.get_fallback_weather(venue, date_obj)
        # Query Open-Meteo Archive API
        lat, lon = coords
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={api_date_str}&end_date={api_date_str}&daily=temperature_2m_max,relative_humidity_2m_mean&timezone=auto"
        
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) IPL Runs Predictor Agent'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            if "daily" in data and "temperature_2m_max" in data["daily"] and len(data["daily"]["temperature_2m_max"]) > 0:
                temp = data["daily"]["temperature_2m_max"][0]
                humidity = data["daily"]["relative_humidity_2m_mean"][0]
                
                # Check for None values from API
                if temp is None:
                    temp, _ = self.get_fallback_weather(venue, date_obj)
                if humidity is None:
                    _, humidity = self.get_fallback_weather(venue, date_obj)
                    
                # Cache results
                self.cache[cache_key] = {"temp": temp, "humidity": humidity}
                self.save_cache()
                return temp, humidity
        except Exception as e:
            # Silent fallback on API error/no connection
            pass
            
        # Fall back to monthly averages if API fails
        temp, humidity = self.get_fallback_weather(venue, date_obj)
        return temp, humidity
if __name__ == "__main__":
    # Test script
    lookup = WeatherPitchLookup()
    print("Testing Wankhede Stadium Pitch:", lookup.get_pitch_type("Wankhede Stadium"))
    print("Testing M Chinnaswamy Pitch:", lookup.get_pitch_type("M Chinnaswamy Stadium"))
    print("Testing Hyderabad Weather (2017-04-05):", lookup.get_weather("Rajiv Gandhi International Stadium, Uppal", "2017-04-05", use_api=True))
    print("Testing Fallback Mumbai Weather (2017-05-15, API=False):", lookup.get_weather("Wankhede Stadium", "2017-05-15", use_api=False))