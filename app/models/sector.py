from app import db
from sqlalchemy.exc import IntegrityError

class Sector(db.Model):
    __tablename__ = 'sectores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    @staticmethod
    def get_next_id():
        ids_existentes = db.session.query(Sector.id).order_by(Sector.id).all()
        ids_existentes = [id[0] for id in ids_existentes] 
        siguiente_id = 1 
        for i in ids_existentes:
            if i != siguiente_id:
                break
            siguiente_id += 1
        return siguiente_id

    @classmethod
    def create(cls, nombre):
        siguiente_id = cls.get_next_id()
        nuevo_sector = cls(id=siguiente_id, nombre=nombre)
        try:
            db.session.add(nuevo_sector)
            db.session.commit()
            return nuevo_sector
        except IntegrityError:
            db.session.rollback()
            raise ValueError("No se pudo insertar el sector. Verifica los datos ingresados.")
