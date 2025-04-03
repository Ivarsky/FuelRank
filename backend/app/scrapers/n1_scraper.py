import requests
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
import os
import time
from app.scrapers.base_scraper import BaseScraper

#TODO: n1 EV charging prices

class N1Scraper(BaseScraper):
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv("N1_API_URL")
        self.contact_data = os.getenv("CONTACT")
        
    #TODO: normalize and fallback for get_coordinates
    def get_coordinates(self, address):
        try:
            params ={
                "q": address,
                "format": "json",
                "limit": 1
            }
            headers = {
                "User-Agent": f"FuelRank ({self.contact_data})"
            }

            response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
            response.raise_for_status()

            data = response.json()

            if data:
                print(f"Coords for {address} found")
                return float(data[0]["lon"]), float(data[0]["lat"])
            else: 
                print(f"ERROR, no coords found for {address}")
                return None, None


        except Exception as e:
            print(f"Geocodifying error '{address}: {e}")

    def get_static_info(self):
        response = requests.post(self.api_url)
        response.raise_for_status()

        stations_raw = response.json()

        stations = []

        for s in stations_raw:
            try:
                #extracting coordinates
                longitude, latitude = self.get_coordinates(s["Location"])
                time.sleep(1)
                
                stations.append({
                        "station": s["Name"],
                        "address": s["Location"],
                        "longitude": longitude,
                        "latitude": latitude,
                        "region": s["Region"],
                        "url": s["Url"],
                    })
            except Exception as e:
                print(f"Error in station '{s.get('Name', '???')}': {e}")
                continue
    
        self.save_to_json({"stations": stations}, "n1_static.json")  

    def update_prices(self, static_filename="n1_static.json"):
        with open(static_filename, "r", encoding="utf-8") as f:
            static_data = json.load(f)
        
        response = requests.post(self.api_url)
        response.raise_for_status()
        stations_dynamic = response.json()

        stations_aux = {s["Name"]: s for s in stations_dynamic}

        updated = []

        for station in static_data["stations"]:
            station_api_data = stations_aux.get(station["station"])

            if not station_api_data:
                print(f"No data for {station['station']}")
                continue

            gas_price = float(station_api_data["GasPrice"].replace(",", ".")) if station_api_data.get("GasPrice") else None
            diesel_price = float(station_api_data["DiselPrice"].replace(",", ".")) if station_api_data.get("DiselPrice") else None
            colored_disel_price = float(station_api_data["ColoredDiselPrice"].replace(",", ".")) if station_api_data.get("ColoredDiselPrice") else None

            station.update({
                "gas_price": gas_price,
                "diesel_price": diesel_price,
                "colored_disel_price": colored_disel_price,
                "shipping_fuel_price": None,
                "gas_discount": None,
                "diesel_discount": None,
                "colored_diesel_discount": None,
                "shipping_fuel_discount": None
            })

            updated.append(station)

        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.save_to_json({
            "timestamp": timestamp,
            "stations": updated
        }, "n1_stations_prices.json")

        print(f"Updated prices for {len(updated)} stations at {timestamp}")


if __name__ == "__main__":
    scraper = N1Scraper()
    #scraper.get_static_info()
    scraper.update_prices()