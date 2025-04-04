import requests
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
import os
import time
import logging
from app.scrapers.base_scraper import BaseScraper

class ObScraper(BaseScraper):
        def __init__(self):
            super().__init__()
            self.api_url = os.getenv("OB_API_URL")
            self.contact_data = os.getenv("CONTACT")
        
        def get_coordinates(self, location_data):
            try:
                params ={
                    "q": f"OB gas station, {location_data}, Iceland",
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
                    self.logger.info(f"Coords for {location_data} found")
                    return float(data[0]["lon"]), float(data[0]["lat"])
                else: 
                    self.logger.warning(f"No coords found for {location_data}")
                    return None, None
            
            except Exception as e:
                self.logger.error(f"Geocodifying error '{location_data}: {e}")

        def get_static_info(self):
            response = requests.post(self.api_url)
            response.raise_for_status()

            stations_raw = response.json()

            stations = []

            for s in stations_raw:
                try:
                    #extracting coordinates
                    longitude, latitude = self.get_coordinates(s["Name"])
                    time.sleep(1)

                    stations.append({
                        "station": s["Name"],
                        "address": s["Name"],
                        "longitude": longitude,
                        "latitude": latitude,
                        "region": None,
                        "url": None,
                    })
                except Exception as e:
                    self.logger.error(f"in station '{s.get('Name', '???')}': {e}")
                    continue
            
            self.save_to_json({"stations": stations}, "ob_static.json")
        
        def update_prices(self, static_filename="ob_static.json"):
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
                    self.logger.warning(f"No data for {station['station']}")
                    continue

                gas_price = float(station_api_data["PricePetrol"]) if station_api_data.get("PricePetrol") else None
                diesel_price = float(station_api_data["PriceDiesel"]) if station_api_data.get("PriceDiesel") else None
                colored_disel_price = float(station_api_data["ColoredDiesel"]) if station_api_data.get("ColoredDiesel") else None
                metan_price = float(station_api_data["PriceMetan"]) if station_api_data.get("PriceMetan") else None

                station.update({
                "gas_price": gas_price,
                "diesel_price": diesel_price,
                "colored_disel_price": colored_disel_price,
                "metan_price": metan_price,
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
            }, "ob_stations_prices.json")

            self.logger.info(f"Updated prices for {len(updated)} OB stations at {timestamp}")

if __name__ == "__main__":
    scraper = ObScraper()
    scraper.get_static_info()
    scraper.update_prices()


