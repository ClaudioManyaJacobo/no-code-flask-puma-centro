from app import db

class Sector(db.Model):
    __tablename__ = 'sectores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectores.id'), nullable=False)
    sector = db.relationship('Sector', backref='usuarios')

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mes_facturacion = db.Column(db.String(20), nullable=False) # MES ACTUAL
    fecha_emision = db.Column(db.Date, nullable=False) # Fecha Actual
    fecha_vencimiento = db.Column(db.Date, nullable=False) # Puesta por el usuario
    fecha_corte = db.Column(db.Date, nullable=False) # Puesta por el usuario
    consumo_kwh = db.Column(db.Float, nullable=False) # lectura_actual - lectura_anterior
    lectura_actual = db.Column(db.Float, nullable=False) # Puesta por el usuario
    lectura_anterior = db.Column(db.Float, nullable=False) # Puesta por el usuario
    deudas_anteriores = db.Column(db.Float, nullable=False, default=0.0) # Puesta por el usuario
    usuario = db.relationship('Usuario', backref='facturas')

class DetalleConsumo(db.Model):
    __tablename__ = 'detalles_consumo'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    cargo_fijo = db.Column(db.Float, nullable=False) # STATICO = 1.50
    energia_activa = db.Column(db.Float, nullable=False) # CONSUMO * FACTOR ENERGIA
    factor_energia = db.Column(db.Float, nullable=False) # STATICO = 0.6
    alumbrado_publico = db.Column(db.Float, nullable=False) # STATICO = 3.60
    aporte_ley = db.Column(db.Float, nullable=False) # STATICO = 0.40
    igv = db.Column(db.Float, nullable=False) # STATICO = 4.23
    # Relacion con Factura
    factura = db.relationship('Factura', backref='detalles')
    
    # TOTALES POR MES Y TOTAL A PAGAR
    total_mes = db.Column(db.Float, nullable=False)
    """
    cargo_fijo + energia_activa + alumbrado_publico + aporte_ley + igv
    
    """
    total_a_pagar = db.Column(db.Float, nullable=False) # TOTAL MES + DEUDAS ANTERIORES
    
    
