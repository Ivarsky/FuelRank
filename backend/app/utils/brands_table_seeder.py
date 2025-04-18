from app.db import db
from app.models.brand import Brand

BRANDS = {
    "AT": "Atlantsolia",
    "N1": "N1",
    "OB": "Ob",
    "OL": "Olis",
    "OR": "Orkan",
}


def seed_brands_table():
    brands_id_count = 0
    for brand_id, brand_name in BRANDS.items():
        if not db.session.get(Brand, brand_id):
            brand = Brand(id=brand_id, name=brand_name)
            db.session.add(brand)
            brands_id_count += 1
    db.session.commit()
    return brands_id_count
