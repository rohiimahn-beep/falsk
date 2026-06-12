from flask import Flask, render_template, request, make_response
import qrcode
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib import colors
from reportlab.platypus import Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from io import BytesIO

application = Flask(__name__)

pengeluaran = []

@application.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        tanggal = request.form['tanggal']
        kategori = request.form['kategori']
        jumlah = request.form['jumlah']

        data = {
            'tanggal': tanggal,
            'kategori': kategori,
            'jumlah': jumlah
        }

        pengeluaran.append(data)

        total = 0

        for item in pengeluaran:
            total += int(item['jumlah'])

        return render_template(
            'dashboard.html',
            data=pengeluaran,
            total=total
        )

    return render_template('form.html')

@application.route('/pdf')
def pdf():

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from datetime import datetime

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    total = 0

    data_tabel = [
        ["No", "Tanggal", "Kategori", "Jumlah"]
    ]

    for i, item in enumerate(pengeluaran, start=1):

        data_tabel.append([
            str(i),
            item["tanggal"],
            item["kategori"],
            f"Rp {int(item['jumlah']):,}".replace(",", ".")
        ])

        total += int(item["jumlah"])

    tabel = Table(
        data_tabel,
        colWidths=[50,120,150,120]
    )

    tabel.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#6FA36F")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),

        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke)
    ]))

    elemen = []

    elemen.append(
        Paragraph(
            "<para align='center'><font size='22'><b>Laporan Pengeluaran Mahasiswa</b></font></para>",
            styles['Title']
        )
    )

    elemen.append(Spacer(1,20))

    elemen.append(tabel)

    elemen.append(Spacer(1,25))

    elemen.append(
        Paragraph(
            f"<b>Total Pengeluaran : Rp {total:,}</b>",
            styles['Heading2']
        )
    )

    elemen.append(Spacer(1,10))

    elemen.append(
        Paragraph(
            f"Tanggal Cetak : {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles['Normal']
        )
    )

    elemen.append(Spacer(1,30))

    elemen.append(
        Paragraph(
            "<para align='center'>--- Dokumen ini dibuat secara otomatis oleh Sistem Expense Tracker Mahasiswa ---</para>",
            styles['Italic']
        )
    )

    doc.build(elemen)

    pdf = buffer.getvalue()

    buffer.close()

    response = make_response(pdf)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=laporan.pdf'

    return response

@application.route('/preview')
def preview():

    total = 0

    for item in pengeluaran:
        total += int(item["jumlah"])

    now = datetime.now().strftime("%d-%m-%Y %H:%M")

    return render_template(
        "preview.html",
        data=pengeluaran,
        total=total,
        now=now
    )

@application.route('/generate_qr')
def generate_qr():

    img = qrcode.make(
        "https://rohiimah.pythonanywhere.com/pdf"
    )

    img.save("static/qr.png")

    return "QR berhasil dibuat"

if __name__ == '__main__':
    application.run(debug=True)