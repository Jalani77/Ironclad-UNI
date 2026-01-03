from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO
from app.schemas import AuditReport


def generate_audit_pdf(report: AuditReport) -> bytes:
    """
    Generate a PDF report from audit data.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C5282'),
        spaceAfter=30,
    )
    story.append(Paragraph("Degree Audit Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Student Information
    student_info = [
        ["Student Name:", report.student.name],
        ["Student ID:", report.student.student_id],
        ["Email:", report.student.email],
        ["Program:", report.program.name],
    ]
    
    student_table = Table(student_info, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E2E8F0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Overall Progress
    status_color = {
        "completed": colors.green,
        "on_track": colors.blue,
        "at_risk": colors.red
    }.get(report.status, colors.grey)
    
    overall_info = [
        ["Total Credits Required:", f"{report.total_credits_required}"],
        ["Total Credits Completed:", f"{report.total_credits_completed}"],
        ["Progress:", f"{report.overall_percentage}%"],
        ["Status:", report.status.upper().replace("_", " ")],
        ["Graduation Eligible:", "YES" if report.graduation_eligible else "NO"],
    ]
    
    overall_table = Table(overall_info, colWidths=[2.5*inch, 1.5*inch])
    overall_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(overall_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Requirements Detail
    story.append(Paragraph("Requirement Details", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    for req in report.requirements:
        req_data = [
            [req.requirement_name, "", "", ""],
            ["Type:", req.requirement_type, "Credits Required:", f"{req.credits_required}"],
            ["Credits Completed:", f"{req.credits_completed}", "Progress:", f"{req.percentage}%"],
            ["Status:", "MET" if req.is_met else "NOT MET", "", ""],
        ]
        
        req_table = Table(req_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        req_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('SPAN', (0, 0), (-1, 0)),
        ]))
        story.append(req_table)
        
        # Completed courses
        if req.completed_courses:
            story.append(Spacer(1, 0.1*inch))
            completed_text = "Completed: " + ", ".join([f"{c.course_code}" for c in req.completed_courses])
            story.append(Paragraph(completed_text, styles['Normal']))
        
        # Missing courses
        if req.missing_courses:
            story.append(Spacer(1, 0.05*inch))
            missing_text = "Missing: " + ", ".join([f"{c.course_code}" for c in req.missing_courses])
            story.append(Paragraph(missing_text, styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
