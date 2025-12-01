from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch

c = canvas.Canvas("aruco_onepager.pdf", pagesize=(35*cm, 35*cm))

# Image positions and sizes (in inches)
images = [
    ("aruco_marker_0.png", 30.5, 22, 4),    # x, y, width
    ("aruco_marker_1.png", 30.5, -8, 4),
    ("aruco_marker_2.png", 0.5, 22, 4),
    ("aruco_marker_3.png", 0.5, -8, 4),
]

for img, x, y, width in images:
    c.drawImage(img, x*cm, y*cm, width=width*cm, preserveAspectRatio=True)

c.save()
