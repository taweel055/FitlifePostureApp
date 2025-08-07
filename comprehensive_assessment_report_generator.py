#!/usr/bin/env python3
"""
Comprehensive Assessment Report Generator
Focuses on the 6-test protocol with detailed clinical assessments
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Flowable, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

class ComprehensiveAssessmentReportGenerator:
    def __init__(self):
        """Initialize the comprehensive assessment report generator"""
        self.page_width, self.page_height = A4
        self._create_styles()
        
    def _create_styles(self):
        """Create custom styles for the comprehensive assessment report"""
        self.styles = getSampleStyleSheet()
        
        # Main title style
        self.title_style = ParagraphStyle(
            'MainTitle',
            parent=self.styles['Title'],
            fontSize=26,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=15,
            spaceBefore=25,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8,
            backColor=colors.HexColor('#f7fafc')
        )
        
        # Test header style
        self.test_header_style = ParagraphStyle(
            'TestHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2b6cb0'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # Clinical note style
        self.clinical_style = ParagraphStyle(
            'Clinical',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=8,
            fontName='Helvetica-Oblique',
            leftIndent=20,
            backColor=colors.HexColor('#f0f4f8'),
            borderWidth=1,
            borderColor=colors.HexColor('#cbd5e0'),
            borderPadding=6
        )

    def _safe_append(self, story, element):
        """Safely append element to story"""
        if element is not None:
            story.append(element)

    def generate_comprehensive_report(self, patient_data, complete_assessment_results, 
                                    traditional_measurements=None, exercise_recommendations=None, output_path="comprehensive_assessment_report.pdf"):
        """Generate comprehensive 6-test assessment report"""
        try:
            # Ensure all parameters are safe
            patient_data = patient_data or {}
            complete_assessment_results = complete_assessment_results or {}
            traditional_measurements = traditional_measurements or {}
            exercise_recommendations = exercise_recommendations or []
            
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Build story
            story = []
            
            # Header with clinic branding
            story.extend(self._create_header())
            
            # Title
            self._safe_append(story, Paragraph("COMPREHENSIVE MOVEMENT & FLEXIBILITY ASSESSMENT", self.title_style))
            self._safe_append(story, Spacer(1, 20))
            
            # Patient Information Section
            story.extend(self._create_patient_info_section(patient_data))
            
            # Assessment Overview
            story.extend(self._create_assessment_overview_section(complete_assessment_results))
            
            # Detailed Test Results
            story.extend(self._create_detailed_test_results_section(complete_assessment_results, patient_data.get('age', 30)))
            
            # Clinical Summary & Recommendations
            story.extend(self._create_clinical_summary_section(complete_assessment_results, exercise_recommendations))
            
            # Traditional Posture Measurements (if available)
            if traditional_measurements:
                story.extend(self._create_traditional_measurements_section(traditional_measurements))
            
            # Footer
            self._safe_append(story, self._create_footer())
            
            # Build PDF
            doc.build(story)
            print(f"✅ Comprehensive assessment report generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating comprehensive report: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_header(self):
        """Create professional header with logo"""
        elements = []
        
        # Try multiple logo paths
        logo_paths = [
            "/Users/abdallah/Downloads/logo.pdf",
            "./logo.pdf",
            "logo.pdf",
            "/Users/abdallah/Desktop/logo.pdf"
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    # Try to create logo placeholder first (safer approach)
                    # Create a styled header with logo placeholder
                    header_data = [
                        ['🏥 LOGO', 'FITLIFE POSTURE CLINIC\nMovement & Flexibility Specialists', 
                         'Assessment Date: ' + datetime.now().strftime('%B %d, %Y') + '\nReport ID: ' + datetime.now().strftime('%Y%m%d-%H%M%S')]
                    ]
                    
                    header_table = Table(header_data, colWidths=[1.5*inch, 3.2*inch, 2.3*inch])
                    header_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (0, 0), 16),
                        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (1, 0), (1, 0), 14),
                        ('FONTNAME', (2, 0), (2, 0), 'Helvetica'),
                        ('FONTSIZE', (2, 0), (2, 0), 10),
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#2b6cb0')),
                        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#1a365d')),
                        ('TEXTCOLOR', (2, 0), (2, 0), colors.HexColor('#4a5568')),
                        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e6f3ff')),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                    ]))
                    
                    elements.append(header_table)
                    print(f"✅ Professional header created with logo placeholder (Logo found at: {logo_path})")
                    logo_loaded = True
                    break
                    
                except Exception as e:
                    print(f"⚠️ Could not process logo at {logo_path}: {e}")
                    continue
        
        if not logo_loaded:
            print("⚠️ No logo file accessible, using enhanced text header")
            # Fallback to enhanced text-only header
            elements.append(self._create_enhanced_text_header())
        
        # Add separator line
        elements.append(Spacer(1, 10))
        
        return elements

    def _create_text_header(self):
        """Create text-only header as fallback"""
        header_data = [
            ['FITLIFE POSTURE CLINIC', 'Assessment Date: ' + datetime.now().strftime('%B %d, %Y')],
            ['Movement & Flexibility Specialists', 'Report ID: ' + datetime.now().strftime('%Y%m%d-%H%M%S')]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 14),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#4a5568')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return header_table

    def _create_enhanced_text_header(self):
        """Create enhanced text-only header with professional styling"""
        header_data = [
            ['🏥 FITLIFE POSTURE CLINIC', 'Assessment Date: ' + datetime.now().strftime('%B %d, %Y')],
            ['Movement & Flexibility Specialists', 'Report ID: ' + datetime.now().strftime('%Y%m%d-%H%M%S')]
        ]
        
        header_table = Table(header_data, colWidths=[4.5*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTSIZE', (0, 1), (0, 1), 12),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#4a5568')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ]))
        
        return header_table

    def _create_patient_info_section(self, patient_data):
        """Create patient information section"""
        elements = []
        
        elements.append(Paragraph("PATIENT INFORMATION", self.section_header_style))
        
        patient_info_data = [
            ['Patient Name:', patient_data.get('name', 'N/A'), 'Age:', str(patient_data.get('age', 'N/A')) + ' years'],
            ['Gender:', patient_data.get('gender', 'N/A'), 'Height:', patient_data.get('height', 'N/A')],
            ['Weight:', patient_data.get('weight', 'N/A'), 'Assessment Date:', datetime.now().strftime('%Y-%m-%d')],
        ]
        
        patient_table = Table(patient_info_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _create_assessment_overview_section(self, complete_assessment_results):
        """Create assessment overview with summary scores"""
        elements = []
        
        elements.append(Paragraph("ASSESSMENT OVERVIEW", self.section_header_style))
        
        if not complete_assessment_results:
            elements.append(Paragraph("No assessment data available.", self.normal_style))
            return elements
        
        # Calculate category scores
        flexibility_tests = ['neck_flexibility', 'hip_flexibility', 'chest_flexibility', 'hamstring_flexibility']
        movement_tests = ['functional_squat', 'single_leg_balance']
        
        flexibility_scores = [complete_assessment_results[test].score for test in flexibility_tests if test in complete_assessment_results]
        movement_scores = [complete_assessment_results[test].score for test in movement_tests if test in complete_assessment_results]
        
        avg_flexibility = round(sum(flexibility_scores) / len(flexibility_scores), 1) if flexibility_scores else 0
        avg_movement = round(sum(movement_scores) / len(movement_scores), 1) if movement_scores else 0
        overall_score = round((avg_flexibility + avg_movement) / 2, 1) if (flexibility_scores or movement_scores) else 0
        
        # Summary table
        summary_data = [
            ['Assessment Category', 'Score', 'Interpretation', 'Priority Level'],
            ['Overall Assessment', f"{overall_score}/10", self._get_score_interpretation(overall_score), self._get_priority_level(overall_score)],
            ['Flexibility Tests (4 tests)', f"{avg_flexibility}/10", self._get_score_interpretation(avg_flexibility), self._get_priority_level(avg_flexibility)],
            ['Movement Quality (2 tests)', f"{avg_movement}/10", self._get_score_interpretation(avg_movement), self._get_priority_level(avg_movement)]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.2*inch, 1*inch, 1.8*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0'))
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 15))
        
        # Clinical alerts
        red_flags = [result for result in complete_assessment_results.values() if result.score < 4]
        if red_flags:
            elements.append(Paragraph("🚨 IMMEDIATE ATTENTION REQUIRED", self.test_header_style))
            alert_text = f"<b>{len(red_flags)} test(s)</b> scored below 4/10, indicating significant dysfunction requiring immediate intervention."
            elements.append(Paragraph(alert_text, self.clinical_style))
            elements.append(Spacer(1, 15))
        
        return elements

    def _create_detailed_test_results_section(self, complete_assessment_results, patient_age):
        """Create detailed results for each of the 6 tests"""
        elements = []
        
        elements.append(Paragraph("DETAILED TEST RESULTS", self.section_header_style))
        
        # Test definitions with protocols
        test_protocols = {
            'neck_flexibility': {
                'name': 'Neck Flexibility Assessment',
                'duration': '20 seconds',
                'target_formula': f'67.54° - 0.50 × {patient_age} = {67.54 - 0.50 * patient_age:.1f}°',
                'protocol': 'Patient performs maximum cervical rotation while maintaining neutral spine alignment.',
                'clinical_significance': 'Assesses cervical mobility, upper crossed syndrome, and postural adaptation patterns.'
            },
            'hip_flexibility': {
                'name': 'Hip Flexibility Assessment',
                'duration': '30 seconds',
                'target_formula': 'Hip flexor length assessment',
                'protocol': 'Modified Thomas test position evaluating hip flexor tightness and compensation patterns.',
                'clinical_significance': 'Identifies hip flexor restrictions contributing to anterior pelvic tilt and lower back dysfunction.'
            },
            'chest_flexibility': {
                'name': 'Chest Flexibility Assessment', 
                'duration': '20 seconds',
                'target_formula': 'Postural health evaluation',
                'protocol': 'Shoulder horizontal adduction assessment measuring pectoral muscle length and thoracic mobility.',
                'clinical_significance': 'Evaluates postural adaptations, forward head posture, and upper crossed syndrome patterns.'
            },
            'hamstring_flexibility': {
                'name': 'Hamstring Flexibility Assessment',
                'duration': '20 seconds', 
                'target_formula': 'Posterior chain analysis',
                'protocol': 'Straight leg raise assessment measuring hamstring length and neural tension.',
                'clinical_significance': 'Assesses posterior chain flexibility, pelvic mechanics, and lower extremity function.'
            },
            'functional_squat': {
                'name': 'Functional Squat Assessment',
                'duration': '45 seconds',
                'target_formula': 'Movement quality scoring (1-10)',
                'protocol': 'Overhead squat assessment evaluating multi-planar movement patterns and compensations.',
                'clinical_significance': 'Comprehensive movement screen identifying kinetic chain dysfunctions and stability deficits.'
            },
            'single_leg_balance': {
                'name': 'Single-Leg Balance Assessment',
                'duration': '60 seconds',
                'target_formula': 'Proprioceptive control assessment',
                'protocol': 'Unilateral stance assessment measuring postural control and neuromuscular stability.',
                'clinical_significance': 'Evaluates proprioceptive function, ankle stability, and fall risk factors.'
            }
        }
        
        for test_name, result in complete_assessment_results.items():
            if test_name in test_protocols:
                protocol = test_protocols[test_name]
                
                # Test header
                elements.append(Paragraph(protocol['name'], self.test_header_style))
                
                # Test details table
                test_details_data = [
                    ['Duration:', protocol['duration'], 'Score:', f"{result.score:.1f}/10"],
                    ['Target:', protocol['target_formula'], 'Measurement:', f"{result.raw_measurement:.1f}°" if result.raw_measurement > 0 else "Qualitative"],
                    ['Status:', self._get_score_interpretation(result.score), 'Priority:', self._get_priority_level(result.score)]
                ]
                
                test_table = Table(test_details_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 1.8*inch])
                test_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ]))
                
                elements.append(test_table)
                elements.append(Spacer(1, 8))
                
                # Protocol description
                elements.append(Paragraph(f"<b>Protocol:</b> {protocol['protocol']}", self.normal_style))
                
                # Clinical significance
                elements.append(Paragraph(f"<b>Clinical Significance:</b> {protocol['clinical_significance']}", self.clinical_style))
                
                # Clinical interpretation
                if result.clinical_interpretation:
                    elements.append(Paragraph(f"<b>Assessment Finding:</b> {result.clinical_interpretation}", self.normal_style))
                
                # Dysfunction flags
                if result.dysfunction_flags:
                    dysfunction_text = ", ".join(result.dysfunction_flags)
                    elements.append(Paragraph(f"<b>Identified Dysfunctions:</b> {dysfunction_text}", self.clinical_style))
                
                elements.append(Spacer(1, 15))
        
        return elements

    def _create_clinical_summary_section(self, complete_assessment_results, exercise_recommendations):
        """Create clinical summary and recommendations"""
        elements = []
        
        elements.append(Paragraph("CLINICAL SUMMARY & RECOMMENDATIONS", self.section_header_style))
        
        # Priority interventions
        red_flags = [result for result in complete_assessment_results.values() if result.score < 4]
        moderate_flags = [result for result in complete_assessment_results.values() if 4 <= result.score < 6]
        
        if red_flags:
            elements.append(Paragraph("IMMEDIATE INTERVENTIONS REQUIRED", self.test_header_style))
            for result in red_flags:
                test_name = result.test_name.replace('_', ' ').title()
                summary_text = f"• <b>{test_name}</b> (Score: {result.score:.1f}/10): {result.clinical_interpretation}"
                elements.append(Paragraph(summary_text, self.clinical_style))
            elements.append(Spacer(1, 10))
        
        if moderate_flags:
            elements.append(Paragraph("MODERATE PRIORITY INTERVENTIONS", self.test_header_style))
            for result in moderate_flags:
                test_name = result.test_name.replace('_', ' ').title()
                summary_text = f"• <b>{test_name}</b> (Score: {result.score:.1f}/10): Requires attention to prevent progression"
                elements.append(Paragraph(summary_text, self.normal_style))
            elements.append(Spacer(1, 10))
        
        # Exercise recommendations
        if exercise_recommendations:
            elements.append(Paragraph("RECOMMENDED INTERVENTIONS", self.test_header_style))
            
            # Categorize recommendations
            unique_recommendations = list(set(exercise_recommendations))[:12]  # Top 12
            
            for i, recommendation in enumerate(unique_recommendations, 1):
                rec_text = f"{i}. {recommendation}"
                elements.append(Paragraph(rec_text, self.normal_style))
            
            elements.append(Spacer(1, 15))
        
        # Follow-up recommendations
        elements.append(Paragraph("FOLLOW-UP PROTOCOL", self.test_header_style))
        
        total_red_flags = len(red_flags)
        if total_red_flags >= 3:
            followup_text = "Recommend immediate follow-up within 2-4 weeks with comprehensive intervention program."
        elif total_red_flags >= 1:
            followup_text = "Recommend follow-up within 4-6 weeks to monitor intervention effectiveness."
        else:
            followup_text = "Recommend routine follow-up in 8-12 weeks for maintenance and prevention."
        
        elements.append(Paragraph(followup_text, self.clinical_style))
        elements.append(Spacer(1, 15))
        
        return elements

    def _create_traditional_measurements_section(self, measurements):
        """Create traditional posture measurements section"""
        elements = []
        
        elements.append(Paragraph("TRADITIONAL POSTURE MEASUREMENTS", self.section_header_style))
        
        measurement_data = [['Measurement', 'Value', 'Normal Range', 'Status']]
        for measurement, value in measurements.items():
            if isinstance(value, (int, float)):
                status = "✓ Normal" if abs(value) < 5 else "⚠ Attention" if abs(value) < 10 else "❌ Significant"
                measurement_data.append([
                    measurement,
                    f"{value:.1f}°",
                    "< 5°",
                    status
                ])
        
        if len(measurement_data) > 1:
            measurement_table = Table(measurement_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            measurement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0'))
            ]))
            
            elements.append(measurement_table)
            elements.append(Spacer(1, 20))
        
        return elements

    def _create_footer(self):
        """Create professional footer"""
        footer_text = (
            "This assessment was conducted using evidence-based protocols and age-adjusted normative data. "
            "Results should be interpreted by qualified healthcare professionals in conjunction with clinical examination. "
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}."
        )
        
        footer_para = Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=self.normal_style,
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER,
            spaceBefore=30,
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=10,
            backColor=colors.HexColor('#f7fafc')
        ))
        
        return footer_para

    def _get_score_interpretation(self, score):
        """Get clinical interpretation for score"""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Fair"
        else:
            return "Poor"

    def _get_priority_level(self, score):
        """Get priority level for intervention"""
        if score >= 6:
            return "Low"
        elif score >= 4:
            return "Moderate"
        else:
            return "High"