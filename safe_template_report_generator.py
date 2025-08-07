#!/usr/bin/env python3
"""
Safe Template-based Report Generator with better error handling
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

class SafeTemplateReportGenerator:
    def __init__(self):
        """Initialize the safe template-based report generator"""
        self.page_width, self.page_height = A4
        self._create_styles()
        
    def _create_styles(self):
        """Create custom styles matching the template"""
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        # Subheader style
        self.subheader_style = ParagraphStyle(
            'CustomSubheader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        )
        
    def _safe_append(self, story, element):
        """Safely append an element to the story, ensuring it's a flowable"""
        if element is None:
            return
            
        # Check if it's a flowable
        if isinstance(element, Flowable):
            story.append(element)
        elif isinstance(element, str):
            # Convert string to Paragraph
            story.append(Paragraph(element, self.normal_style))
        else:
            # Try to convert to string and then to Paragraph
            try:
                story.append(Paragraph(str(element), self.normal_style))
            except:
                print(f"Warning: Could not add element to story: {type(element)}")
                
    def _create_header(self, canvas, doc):
        """Create page header"""
        canvas.saveState()
        
        # Header background
        canvas.setFillColor(colors.HexColor('#f8f9fa'))
        canvas.rect(0, self.page_height - 1.5*inch, self.page_width, 1.5*inch, fill=1, stroke=0)
        
        # Title
        canvas.setFont('Helvetica-Bold', 24)
        canvas.setFillColor(colors.HexColor('#2c3e50'))
        canvas.drawCentredString(self.page_width/2, self.page_height - 0.8*inch, "Posture Analysis Report")
        
        # Accent line
        canvas.setStrokeColor(colors.HexColor('#3498db'))
        canvas.setLineWidth(3)
        canvas.line(inch, self.page_height - 1.2*inch, self.page_width - inch, self.page_height - 1.2*inch)
        
        canvas.restoreState()
        
    def _create_footer(self, canvas, doc):
        """Create page footer"""
        canvas.saveState()
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#bdc3c7'))
        canvas.setLineWidth(1)
        canvas.line(inch, 0.75*inch, self.page_width - inch, 0.75*inch)
        
        # Footer text
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        
        # Generated date
        canvas.drawString(inch, 0.5*inch, 
                         f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        # System info
        canvas.drawRightString(self.page_width - inch, 0.5*inch,
                              "System: Fitlife Posture Assessment v2.0")
        
        # Page number
        canvas.drawCentredString(self.page_width/2, 0.5*inch, f"Page {doc.page}")
        
        canvas.restoreState()
        
    def generate_report(self, patient_data, measurements, muscle_analysis, 
                       exercise_recommendations, output_path):
        """Generate the professional report with safe error handling"""
        try:
            # Ensure all parameters are dictionaries
            patient_data = patient_data or {}
            measurements = measurements or {}
            muscle_analysis = muscle_analysis or {}
            exercise_recommendations = exercise_recommendations or {}
            
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1.75*inch,
                bottomMargin=1*inch
            )
            
            # Build story
            story = []
            
            # Title
            self._safe_append(story, Paragraph("Posture Assessment Report", self.title_style))
            self._safe_append(story, Spacer(1, 20))
            
            # Patient Information
            self._safe_append(story, Paragraph("Patient Information", self.header_style))
            
            # Create patient info as a table for better formatting
            patient_info_data = [
                ['Name:', patient_data.get('name', 'N/A')],
                ['Gender:', patient_data.get('gender', 'N/A')],
                ['Age:', str(patient_data.get('age', 'N/A'))],
                ['Height:', patient_data.get('height', 'N/A')],
                ['Weight:', patient_data.get('weight', 'N/A')],
                ['Assessment Date:', datetime.now().strftime('%Y-%m-%d')]
            ]
            
            patient_table = Table(patient_info_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            
            self._safe_append(story, patient_table)
            self._safe_append(story, Spacer(1, 30))
            
            # Overall Score
            self._safe_append(story, Paragraph("Overall Assessment", self.header_style))
            
            posture_score = float(measurements.get('Overall Posture Score', 0))
            score_status = 'Excellent' if posture_score >= 90 else 'Good' if posture_score >= 80 else 'Needs Improvement'
            
            # Create score as a table
            score_data = [
                ['Posture Score:', f'{posture_score:.1f}/100'],
                ['Status:', score_status],
                ['Assessment Method:', 'MediaPipe Pose Analysis']
            ]
            
            score_table = Table(score_data, colWidths=[2*inch, 4*inch])
            score_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            self._safe_append(story, score_table)
            self._safe_append(story, Spacer(1, 30))
            
            # Measurements
            if measurements:
                self._safe_append(story, Paragraph("Posture Measurements", self.header_style))
                
                # Create measurements table
                measurement_data = [['Measurement', 'Value', 'Normal Range', 'Status']]
                
                for name, value in measurements.items():
                    if name == 'Overall Posture Score':
                        continue
                        
                    # Get normal range
                    normal_ranges = {
                        'Head Tilt': (0, 3),
                        'Craniovertebral Angle': (49, 59),
                        'Head Shoulder Angle': (45, 60),
                        'Shoulder Height Difference': (0, 1.3),
                        'Shoulder Protraction': (0, 2.5),
                        'Pelvic Tilt': (0, 2),
                        'Anterior Pelvic Tilt': (5, 12),
                        'Knee Alignment': (0, 3),
                        'Spinal Curvature': (20, 45),
                        'Hip Alignment': (0, 2),
                        'Ankle Alignment': (0, 5)
                    }
                    
                    normal_range = normal_ranges.get(name, (0, 5))
                    status = 'Normal' if normal_range[0] <= value <= normal_range[1] else 'Needs Attention'
                    
                    measurement_data.append([
                        name,
                        f'{value:.1f}°',
                        f'{normal_range[0]}-{normal_range[1]}°',
                        status
                    ])
                
                if len(measurement_data) > 1:
                    measurement_table = Table(measurement_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
                    measurement_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    self._safe_append(story, measurement_table)
                    self._safe_append(story, Spacer(1, 30))
            
            # Build PDF
            doc.build(story, onFirstPage=self._create_header, onLaterPages=self._create_header)
            
            return True
            
        except Exception as e:
            print(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
            
            # Create a minimal report as fallback
            try:
                doc = SimpleDocTemplate(output_path, pagesize=A4)
                story = []
                story.append(Paragraph("Posture Assessment Report", self.title_style))
                story.append(Spacer(1, 20))
                story.append(Paragraph("Error generating full report. Please try again.", self.normal_style))
                doc.build(story)
                return True
            except:
                return False

    def generate_enhanced_report(self, patient_data, measurements, muscle_analysis,
                               exercise_recommendations, complete_assessment_results, output_path):
        """Generate enhanced PDF report with 6-test assessment data"""
        try:
            # Ensure all parameters are safe
            patient_data = patient_data or {}
            measurements = measurements or {}
            muscle_analysis = muscle_analysis or {}
            exercise_recommendations = exercise_recommendations or []
            complete_assessment_results = complete_assessment_results or {}
            
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1.75*inch,
                bottomMargin=1*inch
            )
            
            # Build story
            story = []
            
            # Title
            self._safe_append(story, Paragraph("Complete Posture Assessment Report", self.title_style))
            self._safe_append(story, Spacer(1, 20))
            
            # Patient Information
            self._safe_append(story, Paragraph("Patient Information", self.header_style))
            
            patient_info_data = [
                ['Name:', patient_data.get('name', 'N/A')],
                ['Gender:', patient_data.get('gender', 'N/A')],
                ['Age:', str(patient_data.get('age', 'N/A'))],
                ['Height:', patient_data.get('height', 'N/A')],
                ['Weight:', patient_data.get('weight', 'N/A')],
                ['Assessment Date:', datetime.now().strftime('%Y-%m-%d')]
            ]
            
            patient_table = Table(patient_info_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            self._safe_append(story, patient_table)
            self._safe_append(story, Spacer(1, 20))
            
            # NEW: Complete 6-Test Assessment Results
            if complete_assessment_results:
                self._safe_append(story, Paragraph("6-Test Complete Assessment Results", self.header_style))
                
                # Calculate overall scores
                flexibility_tests = ['neck_flexibility', 'hip_flexibility', 'chest_flexibility', 'hamstring_flexibility']
                movement_tests = ['functional_squat', 'single_leg_balance']
                
                flexibility_scores = [complete_assessment_results[test].score for test in flexibility_tests if test in complete_assessment_results]
                movement_scores = [complete_assessment_results[test].score for test in movement_tests if test in complete_assessment_results]
                
                avg_flexibility = round(sum(flexibility_scores) / len(flexibility_scores), 1) if flexibility_scores else 0
                avg_movement = round(sum(movement_scores) / len(movement_scores), 1) if movement_scores else 0
                overall_score = round((avg_flexibility + avg_movement) / 2, 1) if (flexibility_scores or movement_scores) else 0
                
                # Summary scores table
                summary_data = [
                    ['Assessment Category', 'Score', 'Interpretation'],
                    ['Overall Assessment', f"{overall_score}/10", self._get_score_interpretation(overall_score)],
                    ['Flexibility Tests', f"{avg_flexibility}/10", self._get_score_interpretation(avg_flexibility)],
                    ['Movement Quality', f"{avg_movement}/10", self._get_score_interpretation(avg_movement)]
                ]
                
                summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                self._safe_append(story, summary_table)
                self._safe_append(story, Spacer(1, 15))
                
                # Individual test results
                self._safe_append(story, Paragraph("Individual Test Results", self.subheader_style))
                
                test_data = [['Test Name', 'Score', 'Measurement', 'Target', 'Clinical Interpretation']]
                
                for test_name, result in complete_assessment_results.items():
                    display_name = test_name.replace('_', ' ').title()
                    score_str = f"{result.score:.1f}/10"
                    measurement_str = f"{result.raw_measurement:.1f}°" if result.raw_measurement > 0 else "N/A"
                    target_str = f"{result.target_value:.1f}°" if result.target_value > 0 else "N/A"
                    interpretation = result.clinical_interpretation[:50] + "..." if len(result.clinical_interpretation) > 50 else result.clinical_interpretation
                    
                    test_data.append([display_name, score_str, measurement_str, target_str, interpretation])
                
                test_table = Table(test_data, colWidths=[1.3*inch, 0.8*inch, 1*inch, 1*inch, 2.4*inch])
                test_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                self._safe_append(story, test_table)
                self._safe_append(story, Spacer(1, 20))
                
                # Red flags section
                red_flags = [result for result in complete_assessment_results.values() if result.score < 4]
                if red_flags:
                    self._safe_append(story, Paragraph("🚨 Clinical Red Flags", self.subheader_style))
                    for result in red_flags:
                        flag_text = f"• {result.test_name}: Score {result.score:.1f}/10 - {result.clinical_interpretation}"
                        self._safe_append(story, Paragraph(flag_text, self.normal_style))
                    self._safe_append(story, Spacer(1, 15))
            
            # Traditional measurements (if available)
            if measurements:
                self._safe_append(story, Paragraph("Traditional Posture Measurements", self.header_style))
                
                measurement_data = [['Measurement', 'Value', 'Normal Range', 'Status']]
                for measurement, value in measurements.items():
                    if isinstance(value, (int, float)):
                        measurement_data.append([
                            measurement,
                            f"{value:.1f}",
                            "Normal",  # Simplified for now
                            "✓" if abs(value) < 10 else "⚠"
                        ])
                
                if len(measurement_data) > 1:  # Only add if we have data
                    measurement_table = Table(measurement_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
                    measurement_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    self._safe_append(story, measurement_table)
                    self._safe_append(story, Spacer(1, 20))
            
            # Exercise recommendations
            if exercise_recommendations:
                self._safe_append(story, Paragraph("Exercise Recommendations", self.header_style))
                
                # Deduplicate and limit recommendations - handle both strings and dicts
                unique_recommendations = []
                seen = set()
                for rec in exercise_recommendations:
                    if isinstance(rec, str):
                        if rec not in seen:
                            unique_recommendations.append(rec)
                            seen.add(rec)
                    elif isinstance(rec, dict):
                        # Convert dict to string representation
                        rec_str = str(rec)
                        if rec_str not in seen:
                            unique_recommendations.append(rec_str)
                            seen.add(rec_str)
                    else:
                        # Handle other types
                        rec_str = str(rec)
                        if rec_str not in seen:
                            unique_recommendations.append(rec_str)
                            seen.add(rec_str)

                # Limit to top 10
                unique_recommendations = unique_recommendations[:10]
                
                for i, recommendation in enumerate(unique_recommendations, 1):
                    rec_text = f"{i}. {recommendation}"
                    self._safe_append(story, Paragraph(rec_text, self.normal_style))
                
                self._safe_append(story, Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            print(f"✅ Enhanced report generated successfully with {len(complete_assessment_results)} assessment tests")
            return True
            
        except Exception as e:
            print(f"❌ Error generating enhanced report: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic report
            return self.generate_report(patient_data, measurements, muscle_analysis, exercise_recommendations, output_path)

    def _get_score_interpretation(self, score):
        """Get clinical interpretation for score"""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Fair - Needs Attention"
        else:
            return "Poor - Immediate Intervention"