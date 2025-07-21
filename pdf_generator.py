from fpdf import FPDF
from datetime import datetime

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Чек заказа", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Имя: {data['Имя']}", ln=2)
    pdf.cell(200, 10, txt=f"Телефон: {data['Телефон']}", ln=3)
    pdf.cell(200, 10, txt=f"Сообщение: {data['Сообщение']}", ln=4)
    pdf.cell(200, 10, txt=f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=5)
    file_path = f"/mnt/data/check_{data['Телефон']}.pdf"
    pdf.output(file_path)
    return file_path
