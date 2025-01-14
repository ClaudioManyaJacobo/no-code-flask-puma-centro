from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash, jsonify, send_from_directory
from app.models.factura import Factura
from app.models.consumo import DetalleConsumo
from app.models.usuario import Usuario
from app import db
from datetime import date, datetime
from babel.dates import format_date
import weasyprint
import PyPDF2
import io
import fitz
from PIL import Image
from fpdf import FPDF
import os

factura_bp = Blueprint('factura_bp', __name__)

@factura_bp.route('/', methods=['GET', 'POST'])
def facturas():
    mes_actual = format_date(datetime.now(), "MMMM", locale="es").upper()
    
    if request.method == 'POST':
        try:
            
            # Validar y procesar datos del formulario
            usuario_id = request.form.get('usuario_id')
            mes_facturacion = request.form.get('mes_facturacion')
            fecha_vencimiento = request.form.get('fecha_vencimiento')
            fecha_corte = request.form.get('fecha_corte')
            lectura_actual = request.form.get('lectura_actual')
            lectura_anterior = request.form.get('lectura_anterior')
            deudas_anteriores = request.form.get('deudas_anteriores')

            # Validaciones
            errores = []
            if not usuario_id:
                errores.append("El usuario es obligatorio.")
            if not mes_facturacion:
                errores.append("El mes de facturación es obligatorio.")
            if not fecha_vencimiento:
                errores.append("La fecha de vencimiento es obligatoria.")
            if not fecha_corte:
                errores.append("La fecha de corte es obligatoria.")
            if not lectura_actual or not lectura_actual.isdigit():
                errores.append("La lectura actual debe ser un número válido.")
            if not lectura_anterior or not lectura_anterior.isdigit():
                errores.append("La lectura anterior debe ser un número válido.")
            if not deudas_anteriores or not deudas_anteriores.isdigit():
                errores.append("Las deudas anteriores deben ser un número válido.")

            if errores:
                for error in errores:
                    flash(error, 'danger')
                return redirect(url_for('factura_bp.facturas'))

            # Convertir valores numéricos
            lectura_actual = round(float(lectura_actual), 2)
            lectura_anterior = round(float(lectura_anterior), 2)
            deudas_anteriores = round(float(deudas_anteriores), 2)
            consumo_kwh = round(lectura_actual - lectura_anterior, 2)

            # Obtener el siguiente ID faltante para la Factura
            siguiente_id_factura = Factura.get_next_id()

            # Crear nueva Factura
            nueva_factura = Factura(
                id=siguiente_id_factura,
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
            energia_activa = round(consumo_kwh * factor_energia, 2)
            alumbrado_publico = 3.60
            aporte_ley = 0.40
            igv = 4.23
            total_mes = round(cargo_fijo + energia_activa + alumbrado_publico + aporte_ley + igv, 2)
            total_a_pagar = round(total_mes + deudas_anteriores, 2)

            # Generar imagen binaria desde HTML
            html_file = render_template('factura_pdf.html', factura=nueva_factura, detalles={
                'cargo_fijo': cargo_fijo,
                'energia_activa': energia_activa,
                'factor_energia': factor_energia,
                'alumbrado_publico': alumbrado_publico,
                'aporte_ley': aporte_ley,
                'igv': igv,
                'total_mes': total_mes,
                'total_a_pagar': total_a_pagar
            })
            imagen_binaria = generar_imagen_binaria(html_file)

            # Obtener el siguiente ID faltante para el DetalleConsumo
            siguiente_id_detalle = DetalleConsumo.get_next_id()

            nuevo_detalle = DetalleConsumo(
                id=siguiente_id_detalle,
                factura_id=nueva_factura.id,
                cargo_fijo=cargo_fijo,
                energia_activa=energia_activa,
                factor_energia=factor_energia,
                alumbrado_publico=alumbrado_publico,
                aporte_ley=aporte_ley,
                igv=igv,
                total_mes=total_mes,
                total_a_pagar=total_a_pagar,
                recibo_img=imagen_binaria
            )
            db.session.add(nuevo_detalle)
            db.session.commit()

            flash("Factura creada exitosamente.", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la factura o detalle de consumo: {e}", "danger")

        return redirect(url_for('factura_bp.facturas'))

    # Renderizar lista de facturas y usuarios
    facturas = Factura.query.all()
    usuarios = Usuario.query.all()
    return render_template('factura.html', facturas=facturas, usuarios=usuarios,  mes_actual=mes_actual)

@factura_bp.route('/recibo/mostrar/<int:factura_id>')
def mostrar_recibo(factura_id):
    try:
        # Obtener la factura y el detalle asociado
        factura = Factura.query.get_or_404(factura_id)
        detalle = DetalleConsumo.query.filter_by(factura_id=factura.id).first()

        if not detalle or not detalle.recibo_img:
            return f"El recibo no está disponible para la factura {factura_id}.", 404

        # Crear una respuesta para servir la imagen como archivo
        response = make_response(detalle.recibo_img)
        response.headers.set('Content-Type', 'image/png')  # Cambiar el tipo MIME si es diferente
        response.headers.set('Content-Disposition', 'inline', filename=f'recibo_{factura_id}.png')
        return response

    except Exception as e:
        print(f"Error al mostrar el recibo: {e}")
        return "Error al mostrar el recibo", 500

# Función para generar la imagen binaria
def generar_imagen_binaria(html_content):
    try:
        # 1. Convertir HTML a PDF en memoria
        pdf_data = weasyprint.HTML(string=html_content).write_pdf()

        # 2. Usar PyPDF2 para eliminar la primera página del PDF
        pdf_no_first_page = remove_first_page(pdf_data)

        # 3. Recortar la página del PDF según las coordenadas especificadas
        cropped_pdf = crop_pdf_page(pdf_no_first_page, [119, 117, 522, 668.4])

        # 4. Convertir el PDF recortado a una imagen con calidad 4K
        imagen_binaria = pdf_to_image(cropped_pdf, scale_factor=4)

        return imagen_binaria
    except Exception as e:
        print(f"Error generando la imagen binaria: {e}")
        return None

# Función para eliminar la primera página de un PDF
def remove_first_page(pdf_data):
    try:
        pdf_io = io.BytesIO(pdf_data)
        reader = PyPDF2.PdfReader(pdf_io)
        writer = PyPDF2.PdfWriter()

        # Agregar todas las páginas excepto la primera
        for page_num in range(1, len(reader.pages)):
            writer.add_page(reader.pages[page_num])

        output_pdf_io = io.BytesIO()
        writer.write(output_pdf_io)
        return output_pdf_io.getvalue()
    except Exception as e:
        print(f"Error eliminando la primera página del PDF: {e}")
        return None

# Función para recortar una página específica de un PDF
def crop_pdf_page(pdf_data, crop_rect):
    try:
        pdf_io = io.BytesIO(pdf_data)
        pdf_document = fitz.open(stream=pdf_io, filetype="pdf")
        page = pdf_document[0]  # Solo recortar la primera página
        page.set_cropbox(crop_rect)

        output_pdf_io = io.BytesIO()
        pdf_document.save(output_pdf_io)
        return output_pdf_io.getvalue()
    except Exception as e:
        print(f"Error recortando el PDF: {e}")
        return None

# Función para convertir un PDF a imagen en calidad 4K
def pdf_to_image(pdf_data, scale_factor):
    try:
        pdf_io = io.BytesIO(pdf_data)
        pdf_document = fitz.open(stream=pdf_io, filetype="pdf")
        page = pdf_document.load_page(0)  # Primera página después del recorte
        matrix = fitz.Matrix(scale_factor, scale_factor)
        pix = page.get_pixmap(matrix=matrix)
        img_io = io.BytesIO()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(img_io, format="PNG")
        return img_io.getvalue()
    except Exception as e:
        print(f"Error convirtiendo el PDF a imagen 4K: {e}")
        return None


# Ruta para generar el PDF de las facturas del mes
@factura_bp.route('/generar_pdf_facturas', methods=['GET'])
def generar_pdf_facturas():
    try:
        # Crear la carpeta temporal si no existe
        temp_folder = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        # Obtener el mes actual en español
        mes_actual = format_date(datetime.now(), "MMMM", locale="es").upper()

        # Filtrar las facturas por el mes actual
        facturas = Factura.query.filter(Factura.mes_facturacion == mes_actual).all()
        if not facturas:
            return jsonify({"error": f"No hay facturas disponibles para el mes {mes_actual}."}), 404

        pdf = FPDF(orientation="L", unit="mm", format="A4")

        # Configuración de página A4 horizontal
        page_width = 297  # mm
        page_height = 210  # mm
        dpi = 300  # Resolución para cálculos de tamaño

        # Procesar las facturas en pares
        for i in range(0, len(facturas), 2):
            pdf.add_page()

            # Procesar imágenes de dos facturas por página
            for j in range(2):
                if i + j >= len(facturas):
                    break

                factura = facturas[i + j]
                detalle = DetalleConsumo.query.filter_by(factura_id=factura.id).first()
                if detalle is None or detalle.recibo_img is None:
                    continue

                # Guardar la imagen binaria como archivo temporal
                temp_image_path = os.path.join(temp_folder, f"recibo_{factura.id}.png")
                with open(temp_image_path, 'wb') as f:
                    f.write(detalle.recibo_img)

                # Cargar la imagen y ajustar su tamaño
                image = Image.open(temp_image_path)
                if image.mode != "RGB":
                    image = image.convert("RGB")

                img_width, img_height = image.size
                max_img_width = (page_width / 2 - 15) * dpi / 25.4
                max_img_height = (page_height - 10) * dpi / 25.4
                scale_w = max_img_width / img_width
                scale_h = max_img_height / img_height
                scale = min(scale_w, scale_h)

                new_width = int(img_width * scale)
                new_height = int(img_height * scale)

                # Ajustar posición de la imagen en la página
                x_offset = (page_width / 2 - (new_width * 25.4 / dpi)) / 2 if j == 0 else page_width / 2 + 7.5
                y_offset = (page_height - (new_height * 25.4 / dpi)) / 2

                # Guardar la imagen temporal escalada
                image.save(temp_image_path, quality=100)

                # Colocar la imagen en el PDF
                pdf.image(temp_image_path, x=x_offset, y=y_offset, w=(new_width * 25.4 / dpi), h=(new_height * 25.4 / dpi))

        # Guardar el PDF generado en la carpeta temporal
        pdf_path = os.path.join(temp_folder, 'facturas_todas.pdf')
        print(f"Ruta completa del archivo PDF: {pdf_path}")
        pdf.output(pdf_path)

        # Retornar la ruta relativa del PDF
        return jsonify({
            "mes": mes_actual,
            "pdf_path": "/facturas/temp/facturas_todas.pdf"
        })
        
    except Exception as e:
        print(f"Error al generar el PDF: {e}")
        return jsonify({"error": "Error al generar el PDF."}), 500

@factura_bp.route('/temp/<path:filename>', methods=['GET'])
def serve_pdf(filename):
    try:
        temp_folder = os.path.join(os.getcwd(), 'temp')
        return send_from_directory(temp_folder, filename)
    except Exception as e:
        print(f"Error al servir el archivo PDF: {e}")
        return "El archivo no se pudo encontrar o acceder.", 404
    
    
@factura_bp.route('/eliminar_todos', methods=['POST'])
def eliminar_todos():
    try:
        # Confirmar la eliminación mediante un parámetro en el formulario
        confirmacion = request.form.get('confirmacion')
        if confirmacion != 'CONFIRMAR':
            flash("Debe confirmar la eliminación ingresando 'CONFIRMAR' en el formulario.", "danger")
            return redirect(url_for('factura_bp.facturas'))

        # Eliminar todos los registros de DetalleConsumo
        num_detalles = DetalleConsumo.query.delete()

        # Eliminar todos los registros de Factura
        num_facturas = Factura.query.delete()

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash(f"Se eliminaron {num_detalles} detalles de consumo y {num_facturas} facturas correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar los datos: {e}", "danger")

    return redirect(url_for('factura_bp.facturas'))
