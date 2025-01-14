import weasyprint
import PyPDF2
import io
import fitz  # PyMuPDF
from PIL import Image
import os
from fpdf import FPDF

# Función principal que combina todas las funcionalidades
def html_to_pdf_with_images(html_file_path, output_pdf_path, crop_rect, scale_factor=4):
    # 1. Convertir HTML a PDF en memoria
    pdf_data = weasyprint.HTML(html_file_path).write_pdf()

    # Usar io.BytesIO para crear un objeto de flujo en memoria a partir de los datos PDF
    pdf_io = io.BytesIO(pdf_data)

    # 2. Usar PyPDF2 para eliminar la primera página del PDF
    reader = PyPDF2.PdfReader(pdf_io)
    writer = PyPDF2.PdfWriter()

    # Agregar todas las páginas excepto la primera
    for page_num in range(1, len(reader.pages)):
        writer.add_page(reader.pages[page_num])

    # Guardar el PDF resultante temporalmente
    temp_pdf_path = "temp_result.pdf"
    with open(temp_pdf_path, 'wb') as output_pdf_file:
        writer.write(output_pdf_file)

    # 3. Recortar la página del PDF según las coordenadas especificadas
    cropped_pdf_path = "temp_cropped.pdf"
    crop_pdf_page(temp_pdf_path, cropped_pdf_path, crop_rect)

    # 4. Convertir el PDF recortado en una imagen con calidad 4K
    output_image_path = "temp_output_image.png"
    pdf_to_image(cropped_pdf_path, output_image_path, scale_factor)

    # 5. Crear un PDF final con dos imágenes en una sola página
    create_pdf_with_images(output_image_path, output_pdf_path)

    # Limpiar los archivos temporales
    os.remove(temp_pdf_path)
    os.remove(cropped_pdf_path)
    os.remove(output_image_path)
    print(f"PDF generado correctamente: {output_pdf_path}")

# Función para recortar una página específica de un PDF
def crop_pdf_page(input_pdf, output_pdf, crop_rect):
    pdf_document = fitz.open(input_pdf)
    page = pdf_document[0]  # Solo recortar la primera página
    page.set_cropbox(crop_rect)  # crop_rect es un listado con [x0, y0, x1, y1]
    pdf_document.save(output_pdf)

# Función para convertir un PDF en una imagen
def pdf_to_image(input_pdf, output_image_path, scale_factor):
    pdf_document = fitz.open(input_pdf)
    page = pdf_document.load_page(0)  # Solo una página después del recorte
    matrix = fitz.Matrix(scale_factor, scale_factor)
    pix = page.get_pixmap(matrix=matrix)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(output_image_path)

# Función para crear un PDF con dos imágenes en una sola página
def create_pdf_with_images(image_path, output_pdf_path):
    page_width = 297  # mm
    page_height = 210  # mm
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")

    img_width, img_height = image.size
    dpi = 300

    # Ajustar tamaños máximos para las imágenes considerando espacio central
    max_img_width = (page_width / 2 - 15) * dpi / 25.4  # Deja 15 mm de margen (7.5 mm a cada lado del centro)
    max_img_height = (page_height - 10) * dpi / 25.4  # Deja un margen adicional arriba y abajo

    scale_w = max_img_width / img_width
    scale_h = max_img_height / img_height
    scale = min(scale_w, scale_h)

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    # Ajustar los offsets considerando el espacio vacío en el centro
    x_offset_left = (page_width / 2 - (new_width * 25.4 / dpi)) / 2
    x_offset_right = page_width / 2 + (15 / 2)  # Deja 15 mm de espacio en el centro
    y_offset = (page_height - (new_height * 25.4 / dpi)) / 2

    temp_image_path = "temp_image.jpg"
    image.save(temp_image_path, quality=100)

    # Colocar las imágenes en la página
    pdf.image(temp_image_path, x=x_offset_left, y=y_offset, w=(new_width * 25.4 / dpi), h=(new_height * 25.4 / dpi))
    pdf.image(temp_image_path, x=x_offset_right, y=y_offset, w=(new_width * 25.4 / dpi), h=(new_height * 25.4 / dpi))

    pdf.output(output_pdf_path)
    os.remove(temp_image_path)

# Ejemplo de uso
html_file_path = 'index.html'
output_pdf_path = 'salida.pdf'
crop_rectangle = [119, 117, 522, 668.4]
html_to_pdf_with_images(html_file_path, output_pdf_path, crop_rectangle)
