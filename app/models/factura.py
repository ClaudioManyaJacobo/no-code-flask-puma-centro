from app import db
from datetime import date

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mes_facturacion = db.Column(db.String(20), nullable=False)  # MES ACTUAL
    fecha_emision = db.Column(db.Date, nullable=False, default=date.today)  # Fecha Actual
    fecha_vencimiento = db.Column(db.Date, nullable=False)  # Puesta por el usuario
    fecha_corte = db.Column(db.Date, nullable=False)  # Puesta por el usuario
    consumo_kwh = db.Column(db.Float, nullable=False)  # lectura_actual - lectura_anterior
    lectura_actual = db.Column(db.Float, nullable=False)  # Puesta por el usuario
    lectura_anterior = db.Column(db.Float, nullable=False)  # Puesta por el usuario
    deudas_anteriores = db.Column(db.Float, nullable=False, default=0.0)  # Puesta por el usuario
    usuario = db.relationship('Usuario', backref='facturas')

    @staticmethod
    def get_next_id():
        ids_existentes = db.session.query(Factura.id).order_by(Factura.id).all()
        ids_existentes = [id[0] for id in ids_existentes]
        siguiente_id = 1
        for i in ids_existentes:
            if i != siguiente_id:
                break
            siguiente_id += 1
        return siguiente_id
