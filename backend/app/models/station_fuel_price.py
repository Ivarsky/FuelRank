from app import db
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import NUMERIC, PrimaryKeyConstraint
from sqlalchemy.orm import relationship


class StationFuelPrice(db.Model):
    __tablename__ = "station_fuel_price"

    update_date = db.Column(TIMESTAMP(timezone=True), nullable=False)
    id_station = db.Column(
        db.String, db.ForeignKey("stations.id"), nullable=False
    )  # noqa: E731
    id_fuel = db.Column(db.string, db.ForeignKey("fuel.id"), nullable=False)
    price = db.Column(NUMERIC(6, 2), nullable=False)
    discount = db.Column(NUMERIC(6, 2), nullable=True)

    constr_fields = ["update_date", "id_station", "id_fuel"]

    __table_args__ = (
        PrimaryKeyConstraint(*constr_fields, name="station_fuel_price_PK"),
    )

    station = relationship("Station", backref="prices")
    fuel = relationship("Fuel", backref="prices")

    def to_dict(self):
        discount = float(self.discount) if self.discount is not None else None
        return {
            "update_date": self.update_date.isoformat(),
            "id_station": self.id_station,
            "id_fuel": self.id_fuel,
            "price": float(self.price),
            "discount": discount,
        }
