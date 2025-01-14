from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.usuario import Usuario
from app.models.sector import Sector

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/', methods=['GET', 'POST'])
def usuarios():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        sector_id = request.form.get('sector_id', '').strip()

        errores = []
        # Validaciones
        if not nombre:
            errores.append("El nombre del usuario es obligatorio.")
        if not sector_id or not sector_id.isdigit():
            errores.append("Debe seleccionar un sector válido.")
        
        # Validación de unicidad del nombre
        if Usuario.query.filter_by(nombre=nombre).first():
            errores.append("El nombre del usuario ya está registrado. Por favor, elija otro.")

        # Si hay errores, agregarlos a los mensajes flash
        if errores:
            for error in errores:
                flash(error, 'danger')
            usuarios = Usuario.query.all()
            sectores = Sector.query.all()
            return render_template('usuario.html', usuarios=usuarios, sectores=sectores)

        try:
            Usuario.create(nombre=nombre, sector_id=int(sector_id))
            flash("Usuario creado exitosamente.", "success")
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")

        return redirect(url_for('usuario_bp.usuarios'))

    usuarios = Usuario.query.all()
    sectores = Sector.query.all()
    return render_template('usuario.html', usuarios=usuarios, sectores=sectores)
