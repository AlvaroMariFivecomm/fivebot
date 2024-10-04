from typing import List
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
 
class PDFCreator:
    def __init__(self):
        self.pdf = FPDF()
 
    def initialize_pdf(self):
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.add_new_page()
 
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

