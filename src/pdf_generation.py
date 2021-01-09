import os
import shutil
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus.tables import Table, colors
from reportlab.platypus.doctemplate import SimpleDocTemplate

from PyPDF2 import PdfFileMerger



# Default location has been set to the user downloads folder
DIRECTORY = str(Path.home()) + "/" + 'analytics_report'

if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

else:
    shutil.rmtree(DIRECTORY)
    os.makedirs(DIRECTORY)

def generate_pdfs_from_figures(*args):



    filenames = ["2_time_zero.pdf",
                 "3_final_time.pdf",
                 "4_cv_time_zero.pdf",
                 "5_cv_final_time.pdf",
                 "6_fluorescene_change_time_a.pdf",
                 "7_fluorescene_change_time_b.pdf",
                 "8_dual_flash_light.pdf",
                 "9_adjusted.pdf",
                 "10_activity.pdf",
                 "11_potential_hits.pdf"]

    assert(len(filenames)==len(args))

    for filename, fig in zip(filenames, args):
        filename= DIRECTORY + "/"  + filename
        fig.write_image(filename)






def generate_table_page_pdf(DF_temp, final_time, pa, na, ps, ns, z):

    filename= DIRECTORY + "/" + "1_statistic_tables.pdf"

    doc = SimpleDocTemplate(filename,
                            pagesize=(7.35*inch,5.26*inch),
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=45,
                            bottomMargin=30)

    Story=[]
    dataTable = []

    cal_txt= f"Calculations are based on time: <b>{final_time}</b>"
    info_text1= f"WT average is: <b>{pa}</b>"
    info_text2= f"EV average is: <b>{na}</b>"
    info_text3= f"WT standard deviation is: <b>{ps}</b>"
    info_text4= f"EV standard deviation is: <b>{ns}</b>"
    info_text5= f"Z-prime for this plate is: <b>{z}</b>"

    styles=getSampleStyleSheet()

    centered = ParagraphStyle(name = 'centered', fontSize = 10, alignment = TA_CENTER)

    for text in [cal_txt, info_text1, info_text2, info_text3, info_text4, info_text5]:
        Story.append(Paragraph(text, styles["Normal"]))
        Story.append(Spacer(1, 10))

    Story.append(Spacer(1, 12))
    Story.append(Spacer(1, 12))

    Story.append(Paragraph("<b>Table of potential hits</b>", centered))
    Story.append(Spacer(1, 12))

    # table headers
    dataTable.append(DF_temp.columns.str.capitalize().tolist())

    for _, row in DF_temp.iterrows():
        dataTable.append([row[i] for i in range(len(row))])

        table = Table(dataTable,
                      repeatRows=1,
                      style=[
                        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                        ('BOX',(0,0),(-1,-1),1.5,colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('LINEABOVE',(0,2),(-1,-1),0.3,colors.grey),
                        ('LINEBEFORE',(1,0),(-1,-1),1.5,colors.grey),
                        ('FONTSIZE',(0, 0), (-1, -1), 6),
                        ('BACKGROUND', (0, 0), (len(row), 0), colors.lightsteelblue)])

    Story.append(table)
    Story.append(Spacer(1, 20))

    Story.append(Spacer(1, 12))

    # generate the PDF document
    doc.build(Story)





def generate_pdf(*args, final_time, DF_temp, pa, na, ps, ns, z):

    # generate pdfs from plotly figures
    generate_pdfs_from_figures(*args)

    # create the statistics table
    generate_table_page_pdf(DF_temp, final_time, pa, na, ps, ns, z)

    # access the generated pdfs in the directory
    files = ["1_statistic_tables.pdf",
             "2_time_zero.pdf",
             "3_final_time.pdf",
             "4_cv_time_zero.pdf",
             "5_cv_final_time.pdf",
             "6_fluorescene_change_time_a.pdf",
             "7_fluorescene_change_time_b.pdf",
             "8_dual_flash_light.pdf",
             "9_adjusted.pdf",
             "10_activity.pdf",
             "11_potential_hits.pdf"]

    pdfs= [DIRECTORY + "/"  + file for file in files]

    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    pdf_file= DIRECTORY + "/" + "complete_analytics_report.pdf"

    merger.write(pdf_file)
    merger.close()









