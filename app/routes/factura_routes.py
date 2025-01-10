from flask import Blueprint, render_template, request, redirect, url_for, make_response
from app.models import Factura, Usuario, DetalleConsumo
from app import db
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from weasyprint import HTML

factura_bp = Blueprint('factura_bp', __name__)

@factura_bp.route('/', methods=['GET', 'POST'])
def facturas():
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        mes_facturacion = request.form['mes_facturacion']
        fecha_vencimiento = request.form['fecha_vencimiento']
        fecha_corte = request.form['fecha_corte']
        lectura_actual = float(request.form['lectura_actual'])
        lectura_anterior = float(request.form['lectura_anterior'])
        deudas_anteriores = float(request.form['deudas_anteriores'])

        consumo_kwh = lectura_actual - lectura_anterior

        nueva_factura = Factura(
            usuario_id=usuario_id,
            mes_facturacion=mes_facturacion,
            fecha_emision=date.today(),
            fecha_vencimiento=fecha_vencimiento,
            fecha_corte=fecha_corte,
            consumo_kwh=consumo_kwh,
            lectura_actual=lectura_actual,
            lectura_anterior=lectura_anterior,
            deudas_anteriores=deudas_anteriores
        )
        db.session.add(nueva_factura)
        db.session.commit()

        # Crear DetalleConsumo
        cargo_fijo = 1.50
        factor_energia = 0.6
        energia_activa = consumo_kwh * factor_energia
        alumbrado_publico = 3.60
        aporte_ley = 0.40
        igv = 4.23
        total_mes = cargo_fijo + energia_activa + alumbrado_publico + aporte_ley + igv
        total_a_pagar = total_mes + deudas_anteriores

        nuevo_detalle = DetalleConsumo(
            factura_id=nueva_factura.id,
            cargo_fijo=cargo_fijo,
            energia_activa=energia_activa,
            factor_energia=factor_energia,
            alumbrado_publico=alumbrado_publico,
            aporte_ley=aporte_ley,
            igv=igv,
            total_mes=total_mes,
            total_a_pagar=total_a_pagar
        )
        db.session.add(nuevo_detalle)
        db.session.commit()

        return redirect(url_for('factura_bp.facturas'))
    facturas = Factura.query.all()
    usuarios = Usuario.query.all()
    return render_template('factura.html', facturas=facturas, usuarios=usuarios)

@factura_bp.route('/pdf/<int:factura_id>')
def generar_pdf(factura_id):
    # Obtener la factura y sus detalles
    factura = Factura.query.get_or_404(factura_id)
    detalles = DetalleConsumo.query.filter_by(factura_id=factura.id).first()

    # Renderizar el HTML usando la plantilla
    rendered_html = render_template('factura_pdf.html', factura=factura, detalles=detalles)

    # Crear el PDF desde el HTML renderizado
    pdf = HTML(string=rendered_html).write_pdf()

    # Crear la respuesta para descargar el PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=factura_{factura.id}.pdf'

    return response