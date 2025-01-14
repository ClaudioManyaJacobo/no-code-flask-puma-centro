from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.sector import Sector
from app import db

sector_bp = Blueprint('sector_bp', __name__)

@sector_bp.route('/', methods=['GET', 'POST'])
def sectores():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()

        if not nombre:
            flash("El nombre del sector es obligatorio.", "danger")
            return redirect(url_for('sector_bp.sectores'))
        
        # Validar que el nombre del sector no sea duplicado
        if Sector.query.filter_by(nombre=nombre).first():
            flash("El nombre del sector ya está registrado. Por favor, elija otro.", "danger")
            return redirect(url_for('sector_bp.sectores'))
        
        # Calcular el siguiente ID disponible
        siguiente_id = Sector.get_next_id()

        # Crear un nuevo sector con el ID calculado
        nuevo_sector = Sector(id=siguiente_id, nombre=nombre)
        try:
            db.session.add(nuevo_sector)
            db.session.commit()
            flash("Sector agregado con éxito.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar el sector: {str(e)}", "danger")
        
        return redirect(url_for('sector_bp.sectores'))

    sectores = Sector.query.all()
    return render_template('sector.html', sectores=sectores)


@sector_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_sector(id):
    sector = Sector.query.get_or_404(id)
    try:
        db.session.delete(sector)
        db.session.commit()
        flash("Sector eliminado con éxito.", "success")
    except Exception as e:
        db.session.rollback()
        flash("No se pudo eliminar el sector.", "danger")
    
    return redirect(url_for('sector_bp.sectores'))
