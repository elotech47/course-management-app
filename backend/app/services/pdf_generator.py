from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

def generate_rubric_pdf(student_name, session_title, session_date, role, rubric_snapshot, criterion_scores, deductions, feedback_names, raw_score, deduction_total, final_score):
    """
    Generate a PDF of the graded rubric with scores filled in, matching the original rubric format
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=16,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=12,
    )
    
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        spaceAfter=2,
        leftIndent=10,
        textColor=colors.black
    )
    
    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Oblique',
        spaceAfter=6,
        leftIndent=10,
        textColor=colors.HexColor('#4B5563')
    )
    
    # Title
    story.append(Paragraph(f"Grade Sheet - {role}", title_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Student and session info
    info_data = [
        ["Name:", student_name, "Date:", session_date],
    ]
    if role in ['SMT', 'Lead', 'Reporter']:
        info_data.append(["Experiment:", session_title, "Time:", ""])
    elif role == 'TT':
        info_data.append(["Topic:", session_title, "Time:", ""])
    
    info_table = Table(info_data, colWidths=[0.75*inch, 3*inch, 0.75*inch, 2.25*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (1, 0), (1, -1), 0.5, colors.black),
        ('LINEBELOW', (3, 0), (3, -1), 0.5, colors.black),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Process rubric criteria
    section_totals = {}
    
    if rubric_snapshot and 'criteria' in rubric_snapshot:
        for section_name, section_data in rubric_snapshot['criteria'].items():
            # Section header
            story.append(Paragraph(section_name, section_style))
            
            section_score = 0
            section_max = 0
            
            # Check if this section has subsections
            if isinstance(section_data, dict) and 'subsections' in section_data:
                # This is a hierarchical section with subsections
                for subsection_name, subsection_data in section_data['subsections'].items():
                    # Subsection title (the criterion name)
                    display_name = subsection_data.get('name', subsection_name)
                    story.append(Paragraph(display_name, subsection_style))
                    
                    # Description if exists
                    if 'description' in subsection_data and subsection_data['description']:
                        story.append(Paragraph(subsection_data['description'], description_style))
                    
                    # Get the max_points for this subsection (which is the criterion)
                    if 'max_points' in subsection_data:
                        max_points = subsection_data['max_points']
                        criterion_key = f"{section_name}.{subsection_name}"
                        obtained = int(round(criterion_scores.get(criterion_key, 0)))
                        
                        # Create scoring scale row
                        scale_data = [list(range(0, int(max_points) + 1))]
                        
                        # Calculate column widths dynamically based on number of points
                        num_points = int(max_points) + 1
                        col_width = 0.25*inch if num_points <= 11 else 0.2*inch
                        col_widths = [col_width] * num_points
                        
                        scale_table = Table(scale_data, colWidths=col_widths)
                        
                        # Build style list
                        style_list = [
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ]
                        
                        # Highlight the obtained score
                        if 0 <= obtained <= max_points:
                            col_index = int(obtained)
                            style_list.append(('BACKGROUND', (col_index, 0), (col_index, 0), colors.HexColor('#DBEAFE')))
                            style_list.append(('FONTNAME', (col_index, 0), (col_index, 0), 'Helvetica-Bold'))
                            style_list.append(('BOX', (col_index, 0), (col_index, 0), 1.5, colors.HexColor('#1a56db')))
                        
                        scale_table.setStyle(TableStyle(style_list))
                        story.append(scale_table)
                        story.append(Spacer(1, 0.1*inch))
                        
                        section_score += obtained
                        section_max += max_points
            else:
                # Simple section without subsections - criteria are direct children
                # Filter out metadata keys
                metadata_keys = ['description', 'subsections', 'name', 'section', 'type']
                
                for key, value in section_data.items():
                    if key not in metadata_keys and isinstance(value, dict) and 'max_points' in value:
                        # This is a criterion with structure
                        display_name = value.get('name', key)
                        story.append(Paragraph(display_name, subsection_style))
                        
                        # Description if exists
                        if 'description' in value and value['description']:
                            story.append(Paragraph(value['description'], description_style))
                        
                        max_points = value['max_points']
                        criterion_key = f"{section_name}.{key}"
                        obtained = int(round(criterion_scores.get(criterion_key, 0)))
                        
                        # Handle feedback names for YouTube
                        if feedback_names and criterion_key in feedback_names:
                            name_text = f"Feedback for {feedback_names[criterion_key]}"
                            story.append(Paragraph(name_text, description_style))
                        
                        # Create scoring scale row
                        scale_data = [list(range(0, int(max_points) + 1))]
                        
                        # Calculate column widths dynamically
                        num_points = int(max_points) + 1
                        col_width = 0.25*inch if num_points <= 11 else 0.2*inch
                        col_widths = [col_width] * num_points
                        
                        scale_table = Table(scale_data, colWidths=col_widths)
                        
                        # Build style list
                        style_list = [
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ]
                        
                        # Highlight the obtained score
                        if 0 <= obtained <= max_points:
                            col_index = int(obtained)
                            style_list.append(('BACKGROUND', (col_index, 0), (col_index, 0), colors.HexColor('#DBEAFE')))
                            style_list.append(('FONTNAME', (col_index, 0), (col_index, 0), 'Helvetica-Bold'))
                            style_list.append(('BOX', (col_index, 0), (col_index, 0), 1.5, colors.HexColor('#1a56db')))
                        
                        scale_table.setStyle(TableStyle(style_list))
                        story.append(scale_table)
                        story.append(Spacer(1, 0.1*inch))
                        
                        section_score += obtained
                        section_max += max_points
            
            # Section subtotal
            subtotal_data = [[f"Subtotal - {section_name}", "", f"out of {int(section_max)}pts"]]
            subtotal_table = Table(subtotal_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            subtotal_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('LINEABOVE', (2, 0), (2, 0), 0.5, colors.black),
            ]))
            story.append(subtotal_table)
            story.append(Spacer(1, 0.15*inch))
            
            section_totals[section_name] = {'obtained': section_score, 'max': section_max}
    
    # Deductions section
    if deductions and any(deductions.values()):
        story.append(Paragraph("Deductions:", section_style))
        
        for key, value in deductions.items():
            if value > 0:
                deduction_name = key.replace('_', ' ').title()
                deduction_line = f"{deduction_name}"
                deduction_value = f"-{int(round(value))}pts"
                
                deduction_data = [[deduction_line, "", deduction_value]]
                deduction_table = Table(deduction_data, colWidths=[4.5*inch, 0.5*inch, 1*inch])
                deduction_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                    ('LINEBELOW', (2, 0), (2, 0), 0.5, colors.black),
                ]))
                story.append(deduction_table)
        
        story.append(Spacer(1, 0.15*inch))
    
    # Total Grade section
    story.append(Paragraph("d. Total Grade", section_style))
    total_grade_data = [["", f"out of {rubric_snapshot.get('max_points', 0)}pts"]]
    total_grade_table = Table(total_grade_data, colWidths=[4.5*inch, 1.5*inch])
    total_grade_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(total_grade_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Comments section
    story.append(Paragraph("Comments:", section_style))
    comments_data = [["", ""]]
    comments_table = Table(comments_data, colWidths=[6*inch])
    comments_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
    ]))
    story.append(comments_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
