from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Template
import os

def generate_rubric_html(
    student_name: str,
    course_name: str,
    session_info: Dict[str, Any],
    role: str,
    rubric_data: Dict[str, Any],
    criterion_scores: Dict[str, float],
    deductions: Optional[Dict[str, float]],
    comments: Optional[str],
    final_score: float
) -> str:
    """Generate HTML for graded rubric email"""
    
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
            }
            .content {
                background-color: #f9f9f9;
                padding: 20px;
                margin-top: 20px;
                border-radius: 5px;
            }
            .info-section {
                margin-bottom: 20px;
            }
            .info-row {
                display: flex;
                margin-bottom: 10px;
            }
            .info-label {
                font-weight: bold;
                width: 150px;
            }
            .scores-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .scores-table th, .scores-table td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            .scores-table th {
                background-color: #3498db;
                color: white;
            }
            .scores-table tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .deductions {
                background-color: #ffe6e6;
                padding: 15px;
                border-left: 4px solid #e74c3c;
                margin: 15px 0;
            }
            .comments {
                background-color: #e8f5e9;
                padding: 15px;
                border-left: 4px solid #4caf50;
                margin: 15px 0;
            }
            .final-score {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Graded Rubric Report</h1>
            <p>{{ course_name }}</p>
        </div>
        
        <div class="content">
            <div class="info-section">
                <div class="info-row">
                    <span class="info-label">Student:</span>
                    <span>{{ student_name }}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Session:</span>
                    <span>{{ session_title }} - {{ session_date }}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Role:</span>
                    <span>{{ role }}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Graded on:</span>
                    <span>{{ graded_date }}</span>
                </div>
            </div>
            
            <h2>Scoring Breakdown</h2>
            <table class="scores-table">
                <thead>
                    <tr>
                        <th>Criterion</th>
                        <th>Score</th>
                        <th>Max Points</th>
                    </tr>
                </thead>
                <tbody>
                    {% for criterion_id, criterion_info in criteria.items() %}
                    <tr>
                        <td>{{ criterion_info.name }}</td>
                        <td>{{ scores.get(criterion_id, 0) }}</td>
                        <td>{{ criterion_info.max_points }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            {% if deductions %}
            <div class="deductions">
                <h3>Deductions</h3>
                {% for deduction_id, points in deductions.items() %}
                    {% if points > 0 %}
                    <div>
                        <strong>{{ deduction_info[deduction_id].name }}:</strong> -{{ points }} points
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
            {% endif %}
            
            {% if comments %}
            <div class="comments">
                <h3>Instructor Comments</h3>
                <p>{{ comments }}</p>
            </div>
            {% endif %}
        </div>
        
        <div class="final-score">
            <strong>Final Score: {{ final_score }} / {{ max_points }}</strong>
        </div>
        
        <div class="footer">
            <p>This is an automated message from the Course Management System.</p>
            <p>If you have questions about your grade, please contact your instructor.</p>
        </div>
    </body>
    </html>
    """
    
    template = Template(template_str)
    
    html = template.render(
        student_name=student_name,
        course_name=course_name,
        session_title=session_info.get("title", ""),
        session_date=session_info.get("date", ""),
        role=role,
        graded_date=datetime.now().strftime("%B %d, %Y"),
        criteria=rubric_data.get("criteria", {}),
        scores=criterion_scores,
        deductions=deductions or {},
        deduction_info=rubric_data.get("deductions", {}),
        comments=comments or "",
        final_score=final_score,
        max_points=rubric_data.get("max_points", 0)
    )
    
    return html
