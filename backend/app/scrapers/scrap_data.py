from app.scrapers.atlantsolia_scraper import AtlansoliaScraper
from app.scrapers.n1_scraper import N1Scraper
from app.scrapers.olis_ob_scraper import OlisObScraper
from app.scrapers.orkan_scraper import OrkanScraper
import logging

# TODO: take out to constants file?
SCRAPERS = [
    AtlansoliaScraper(),
    N1Scraper(),
    OlisObScraper(),
    OrkanScraper(),
]

logger = logging.getLogger("allscraper")


def get_static_data():
    logger.info("scraping static info")
    for scraper in SCRAPERS:
        scraper.get_static_info()


def update_prices():
    logger.info("updating prices")
    for scraper in SCRAPERS:
        scraper.update_prices()


if __name__ == "__main__":
    get_static_data(),
    update_prices()
