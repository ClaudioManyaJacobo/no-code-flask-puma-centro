from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Usuario, Sector
from app import db

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/', methods=['GET', 'POST'])
def usuarios():
    if request.method == 'POST':
        nombre = request.form['nombre']
        sector_id = request.form['sector_id']
        nuevo_usuario = Usuario(nombre=nombre, sector_id=sector_id)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('usuario_bp.usuarios'))
    usuarios = Usuario.query.all()
    sectores = Sector.query.all()
    return render_template('usuario.html', usuarios=usuarios, sectores=sectores)
