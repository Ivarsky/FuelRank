from app.settings import SCHEMA_NAME
from app import db


class Brand(db.Model):
    __tablename__ = "brands"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    stations = db.relationship("Station", back_populates="brand")

    def __repr__(self):
        return f"<Brand {self.name}>"

    def to_dict(self):
        return {"id": self.id, "name": self.name}
