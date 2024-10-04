from fpdf import FPDF

# Clase PDF personalizada para crear el reporte
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Resumen de Elecciones y Resultados', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def add_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, 0, 1, 'L')

    def add_paragraph(self, text):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, text)

# Función para crear el PDF con elecciones dinámicas
def crear_pdf(elecciones, output_path):
    """
    Crea un archivo PDF con las elecciones y resultados proporcionados.

    :param elecciones: Lista de tuplas con ('eleccion', 'resultado')
    :param output_path: Ruta donde se guardará el archivo PDF
    """
    pdf = PDF()
    pdf.add_page()

    # Agregar título
    pdf.add_title("Elecciones y Resultados del Usuario")

    # Agregar cada elección y su resultado
    for eleccion, resultado in elecciones:
        pdf.add_paragraph(f"{eleccion}")
        pdf.add_paragraph(f"{resultado}")
        pdf.ln(10)

    # Guardar el PDF
    pdf.output(output_path)
    print(f"PDF guardado en: {output_path}")


