from app import db
from datetime import date

class DetalleConsumo(db.Model):
    __tablename__ = 'detalles_consumo'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    cargo_fijo = db.Column(db.Float, nullable=False)  # STATICO = 1.50
    energia_activa = db.Column(db.Float, nullable=False)  # CONSUMO * FACTOR ENERGIA
    factor_energia = db.Column(db.Float, nullable=False)  # STATICO = 0.6
    alumbrado_publico = db.Column(db.Float, nullable=False)  # STATICO = 3.60
    aporte_ley = db.Column(db.Float, nullable=False)  # STATICO = 0.40
    igv = db.Column(db.Float, nullable=False)  # STATICO = 4.23
    total_mes = db.Column(db.Float, nullable=False)  # Calculado
    total_a_pagar = db.Column(db.Float, nullable=False)  # TOTAL MES + DEUDAS ANTERIORES
    recibo_img = db.Column(db.LargeBinary, nullable=True)
    factura = db.relationship('Factura', backref='detalles')

    @staticmethod
    def get_next_id():
        """Calcula el siguiente ID faltante para el modelo DetalleConsumo."""
        ids_existentes = db.session.query(DetalleConsumo.id).order_by(DetalleConsumo.id).all()
        ids_existentes = [id[0] for id in ids_existentes]
        siguiente_id = 1
        for i in ids_existentes:
            if i != siguiente_id:
                break
            siguiente_id += 1
        return siguiente_id
