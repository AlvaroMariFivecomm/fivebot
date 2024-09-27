from typing import List
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np

class PDFCreator:
    def __init__(self):
        self.pdf = FPDF()

    def initialize_pdf(self):
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def add_new_page(self):
        self.pdf.add_page()

    def add_title(self, title: str, font_size: int = 18):
        self.pdf.set_font("Arial", 'B', font_size)
        self.pdf.cell(0, 10, title, ln=True, align='C')

    def add_paragraph(self, text: str, font_size: int = 12):
        self.pdf.set_font("Arial", '', font_size)
        self.pdf.multi_cell(0, 10, text)

    def add_bar_chart(self, data: List[int], chart_title: str, filename: str):
        plt.figure(figsize=(10, 6))
        plt.bar(range(24), data, color='skyblue')
        plt.title(chart_title)
        plt.xlabel('Hours')
        plt.ylabel('Device Count')

        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

        self.pdf.image(filename, x=10, y=None, w=190)

    def save_pdf(self, file_name: str):
        self.pdf.output(file_name)

def create_pdf(aux1, devices_per_hour_aux, devices_per_cell, matrix):
    pdf_creator = PDFCreator()
    pdf_creator.initialize_pdf()

    devices_per_hour_before = [aux1.get(hour, 0) for hour in range(24)]
    devices_per_hour_after = [devices_per_hour_aux.get(hour, 0) for hour in range(24)]

    pdf_creator.add_new_page()
    pdf_creator.add_title('Fivecomm')
    
    # Save each chart to a different file name
    pdf_creator.add_bar_chart(devices_per_hour_before, 'Distribución de Dispositivos por Hora (Antes)', 'chart_before.png')
    pdf_creator.add_bar_chart(devices_per_hour_after, 'Distribución de Dispositivos por Hora (Después)', 'chart_after.png')
    
    pdf_creator.add_new_page()

    pdf_creator.add_title('Resumen de dispositivos por hora:', 18)
    for hour in range(24):
        text = f"Hora {hour}: {devices_per_hour_aux.get(hour, 0)} dispositivos"
        pdf_creator.add_paragraph(text)

    pdf_creator.add_new_page()
    pdf_creator.add_title('Matriz de dispositivos:', 18)
    for cell_id, hours in matrix.items():
        pdf_creator.add_paragraph(f"Celda: {cell_id}")
        for hour, devices in hours.items():
            text = f"  Hora {hour}: {', '.join(devices)}"
            pdf_creator.add_paragraph(text)

    pdf_creator.add_new_page()
    pdf_creator.add_title('Resumen de dispositivos por celda:', 18)
    for cell_id, count in devices_per_cell.items():
        text = f"Celda {cell_id}: {count} dispositivos"
        pdf_creator.add_paragraph(text)

    pdf_creator.save_pdf('output.pdf')
