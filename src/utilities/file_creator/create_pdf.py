# create_pdf.py

# .pdf: portable document format files

from reportlab.pdfgen import canvas

c = canvas.Canvas("./test_files/example.pdf")
c.drawString(100, 750, "Hello, this is a PDF file.")
c.save()