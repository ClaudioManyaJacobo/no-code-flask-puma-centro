from app import db
from sqlalchemy.exc import IntegrityError

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectores.id'), nullable=False)
    sector = db.relationship('Sector', backref='usuarios')

    @staticmethod
    def get_next_id():
        ids_existentes = db.session.query(Usuario.id).order_by(Usuario.id).all()
        ids_existentes = [id[0] for id in ids_existentes]
        siguiente_id = 1
        for i in ids_existentes:
            if i != siguiente_id:
                break
            siguiente_id += 1
        return siguiente_id

    @classmethod
    def create(cls, nombre, sector_id):
        siguiente_id = cls.get_next_id()
        nuevo_usuario = cls(id=siguiente_id, nombre=nombre, sector_id=sector_id)
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            return nuevo_usuario
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Error al crear el usuario: {str(e.orig)}")
