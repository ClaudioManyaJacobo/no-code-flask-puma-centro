from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Sector
from app import db

sector_bp = Blueprint('sector_bp', __name__)

@sector_bp.route('/', methods=['GET', 'POST'])
def sectores():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nuevo_sector = Sector(nombre=nombre)
        db.session.add(nuevo_sector)
        db.session.commit()
        flash("Sector agregado con éxito.", "success")
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
    except:
        flash("No se pudo eliminar el sector.", "danger")
    return redirect(url_for('sector_bp.sectores'))
