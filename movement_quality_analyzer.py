#!/usr/bin/env python3
"""
Enhanced Movement Quality Analyzer
Real-time pose assessment with clinical interpretation and instant feedback
Based on MediaPipe Pose Landmarker with comprehensive movement scoring
"""

import numpy as np
import cv2
import json
import time
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class MovementTest(Enum):
    """Available movement quality tests"""
    NECK_FLEX = "neck_flex"
    HIP_EXTENSION = "hip_extension"
    CHEST_PEC = "chest_pec"
    HAMSTRING = "hamstring"
    SQUAT = "squat"
    SINGLE_LEG_BALANCE = "single_leg_balance"

@dataclass
class MovementScore:
    """Movement quality score with clinical context"""
    raw_angle: float
    normalized_score: float  # 0-10 scale
    asymmetry_penalty: float
    compensation_flags: List[str]
    clinical_interpretation: str
    feedback_message: str
    color_code: Tuple[int, int, int]  # BGR for OpenCV

class MovementQualityAnalyzer:
    """
    Comprehensive movement quality assessment system
    Integrates with existing MediaPipe pose detection
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize movement quality analyzer with configurable thresholds"""
        self.config = self._load_config(config_path)
        self.landmark_buffer = []  # For balance sway analysis
        self.assessment_start_time = None
        
        # Clinical thresholds (configurable)
        self.age_norms = {
            'neck_rom': lambda age: 67.54 - 0.5 * age,
            'hip_extension': lambda age: max(20, 35 - 0.2 * age),
            'chest_horizontal': lambda age: max(30, 45 - 0.15 * age),
            'hamstring_flex': lambda age: max(60, 80 - 0.1 * age)
        }
        
        # Feedback messages (multi-language support)
        self.feedback_messages = {
            'neck_rom_low': {
                'en': "Extend neck range - look up and down slowly",
                'ar': "إرجع لورا شوي، إعمل إطالة للجهة اليمين"
            },
            'squat_valgus': {
                'en': "Drive knees out—imagine ripping the floor apart",
                'ar': "ادفع الركب للخارج - تخيل إنك بتمزق الأرض"
            },
            'balance_sway': {
                'en': "Fix your gaze on a static point and engage core",
                'ar': "ثبت نظرك على نقطة ثابتة وشد عضلات البطن"
            }
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration for clinical thresholds"""
        default_config = {
            "scoring_weights": {
                "rom": 0.4,
                "quality": 0.4,
                "symmetry": 0.2
            },
            "compensation_penalties": {
                "trunk_lean": 2,
                "knee_valgus": 2,
                "excessive_sway": 3
            },
            "thresholds": {
                "asymmetry_tolerance": 5,  # degrees
                "balance_time_target": 30,  # seconds
                "sway_tolerance": 2.0  # cm
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
    
    def angle_3pts(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        """
        Calculate angle ABC (in degrees) given three XYZ points
        Enhanced version with better numerical stability
        """
        ba, bc = a - b, c - b
        
        # Handle zero vectors
        norm_ba, norm_bc = np.linalg.norm(ba), np.linalg.norm(bc)
        if norm_ba == 0 or norm_bc == 0:
            return 0.0
            
        cosang = np.dot(ba, bc) / (norm_ba * norm_bc)
        cosang = np.clip(cosang, -1.0, 1.0)  # Prevent numerical errors
        
        return np.degrees(np.arccos(cosang))
    
    def assess_neck_flexibility(self, landmarks, age: int) -> MovementScore:
        """Assess neck flexibility and forward head posture"""
        try:
            # Get key landmarks
            left_ear = np.array([landmarks[7].x, landmarks[7].y, landmarks[7].z])
            nose = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
            right_ear = np.array([landmarks[8].x, landmarks[8].y, landmarks[8].z])
            
            # Calculate lateral tilt
            lateral_tilt = self.angle_3pts(left_ear, nose, right_ear)
            
            # Normalize against age
            age_norm = self.age_norms['neck_rom'](age)
            normalized_score = min(10, (lateral_tilt / age_norm) * 10)
            
            # Check for compensation patterns
            compensation_flags = []
            if lateral_tilt < age_norm * 0.55:  # Red flag threshold
                compensation_flags.append("forward_head_posture")
                
            # Clinical interpretation
            if normalized_score >= 8:
                interpretation = "Excellent neck mobility"
                feedback = self.feedback_messages.get('neck_excellent', {}).get('en', "Great neck flexibility!")
                color = (0, 255, 0)  # Green
            elif normalized_score >= 6:
                interpretation = "Good neck mobility with minor restrictions"
                feedback = "Continue neck mobility exercises"
                color = (0, 255, 255)  # Yellow
            else:
                interpretation = "Restricted neck mobility - intervention needed"
                feedback = self.feedback_messages['neck_rom_low']['en']
                color = (0, 0, 255)  # Red
                
            return MovementScore(
                raw_angle=lateral_tilt,
                normalized_score=normalized_score,
                asymmetry_penalty=0,  # Could add L/R comparison
                compensation_flags=compensation_flags,
                clinical_interpretation=interpretation,
                feedback_message=feedback,
                color_code=color
            )
            
        except Exception as e:
            return self._create_error_score(f"Neck assessment error: {e}")
    
    def assess_hip_extension(self, landmarks, age: int, side: str = 'right') -> MovementScore:
        """Assess hip extension range of motion"""
        try:
            # Select landmarks based on side
            if side == 'right':
                shoulder_idx, hip_idx, knee_idx = 12, 24, 26
            else:
                shoulder_idx, hip_idx, knee_idx = 11, 23, 25
                
            shoulder = np.array([landmarks[shoulder_idx].x, landmarks[shoulder_idx].y, landmarks[shoulder_idx].z])
            hip = np.array([landmarks[hip_idx].x, landmarks[hip_idx].y, landmarks[hip_idx].z])
            knee = np.array([landmarks[knee_idx].x, landmarks[knee_idx].y, landmarks[knee_idx].z])
            
            # Calculate hip extension angle
            hip_angle = 180 - self.angle_3pts(shoulder, hip, knee)
            
            # Normalize against age
            age_norm = self.age_norms['hip_extension'](age)
            normalized_score = min(10, (hip_angle / age_norm) * 10)
            
            # Check for compensation
            compensation_flags = []
            if hip_angle < 10:  # Tight iliopsoas indicator
                compensation_flags.append("tight_iliopsoas")
                
            # Clinical interpretation
            if normalized_score >= 8:
                interpretation = "Excellent hip extension mobility"
                feedback = "Maintain current hip flexibility"
                color = (0, 255, 0)
            elif normalized_score >= 6:
                interpretation = "Good hip extension with minor tightness"
                feedback = "Continue hip flexor stretching"
                color = (0, 255, 255)
            else:
                interpretation = "Restricted hip extension - likely from prolonged sitting"
                feedback = "Half-kneeling hip-flexor stretch 2×30s/day recommended"
                color = (0, 0, 255)
                
            return MovementScore(
                raw_angle=hip_angle,
                normalized_score=normalized_score,
                asymmetry_penalty=0,
                compensation_flags=compensation_flags,
                clinical_interpretation=interpretation,
                feedback_message=feedback,
                color_code=color
            )
            
        except Exception as e:
            return self._create_error_score(f"Hip extension assessment error: {e}")
    
    def assess_squat_quality(self, landmarks, age: int) -> MovementScore:
        """Comprehensive squat movement quality assessment"""
        try:
            # Get bilateral landmarks
            left_hip = np.array([landmarks[23].x, landmarks[23].y, landmarks[23].z])
            right_hip = np.array([landmarks[24].x, landmarks[24].y, landmarks[24].z])
            left_knee = np.array([landmarks[25].x, landmarks[25].y, landmarks[25].z])
            right_knee = np.array([landmarks[26].x, landmarks[26].y, landmarks[26].z])
            left_ankle = np.array([landmarks[27].x, landmarks[27].y, landmarks[27].z])
            right_ankle = np.array([landmarks[28].x, landmarks[28].y, landmarks[28].z])
            
            # Calculate key angles
            left_knee_angle = self.angle_3pts(left_hip, left_knee, left_ankle)
            right_knee_angle = self.angle_3pts(right_hip, right_knee, right_ankle)
            
            # Check for knee valgus (knees caving in)
            knee_separation = abs(left_knee[0] - right_knee[0])
            hip_separation = abs(left_hip[0] - right_hip[0])
            valgus_ratio = knee_separation / hip_separation if hip_separation > 0 else 1
            
            # Scoring components
            symmetry_score = 10 - abs(left_knee_angle - right_knee_angle)
            valgus_penalty = 3 if valgus_ratio < 0.8 else 0  # Knees too close
            
            # Composite score
            base_score = (left_knee_angle + right_knee_angle) / 2
            normalized_score = min(10, max(0, (base_score / 90) * 10 - valgus_penalty))
            
            # Compensation flags
            compensation_flags = []
            if valgus_ratio < 0.8:
                compensation_flags.append("knee_valgus")
            if abs(left_knee_angle - right_knee_angle) > 10:
                compensation_flags.append("asymmetric_squat")
                
            # Clinical interpretation
            if normalized_score >= 8:
                interpretation = "Excellent squat mechanics"
                feedback = "Perfect squat form - maintain this pattern"
                color = (0, 255, 0)
            elif normalized_score >= 6:
                interpretation = "Good squat with minor compensations"
                feedback = "Focus on knee tracking over toes"
                color = (0, 255, 255)
            else:
                interpretation = "Poor squat mechanics - multiple compensations detected"
                feedback = self.feedback_messages['squat_valgus']['en']
                color = (0, 0, 255)
                
            return MovementScore(
                raw_angle=base_score,
                normalized_score=normalized_score,
                asymmetry_penalty=abs(left_knee_angle - right_knee_angle),
                compensation_flags=compensation_flags,
                clinical_interpretation=interpretation,
                feedback_message=feedback,
                color_code=color
            )
            
        except Exception as e:
            return self._create_error_score(f"Squat assessment error: {e}")
    
    def assess_balance_quality(self, landmarks, duration: float = 30.0) -> MovementScore:
        """Assess single-leg balance with center of pressure analysis"""
        try:
            # Track ankle and pelvis landmarks for sway analysis
            left_ankle = np.array([landmarks[27].x, landmarks[27].y])
            right_ankle = np.array([landmarks[28].x, landmarks[28].y])
            pelvis_center = np.array([
                (landmarks[23].x + landmarks[24].x) / 2,
                (landmarks[23].y + landmarks[24].y) / 2
            ])
            
            # Add to buffer for sway analysis
            self.landmark_buffer.append({
                'timestamp': time.time(),
                'left_ankle': left_ankle,
                'right_ankle': right_ankle,
                'pelvis': pelvis_center
            })
            
            # Keep only recent data (last 30 seconds)
            current_time = time.time()
            self.landmark_buffer = [
                frame for frame in self.landmark_buffer 
                if current_time - frame['timestamp'] <= duration
            ]
            
            if len(self.landmark_buffer) < 30:  # Need minimum data
                return MovementScore(0, 0, 0, [], "Insufficient data", "Hold position longer", (128, 128, 128))
            
            # Calculate sway metrics
            pelvis_positions = np.array([frame['pelvis'] for frame in self.landmark_buffer])
            sway_area = self._calculate_sway_area(pelvis_positions)
            sway_velocity = self._calculate_sway_velocity(pelvis_positions)
            
            # Scoring
            time_held = len(self.landmark_buffer) / 30  # Assuming 30 FPS
            time_score = min(10, (time_held / duration) * 10)
            sway_penalty = min(5, sway_area * 2)  # Penalty for excessive sway
            
            normalized_score = max(0, time_score - sway_penalty)
            
            # Compensation flags
            compensation_flags = []
            if sway_area > 2.0:
                compensation_flags.append("excessive_sway")
            if sway_velocity > 1.5:
                compensation_flags.append("unstable_balance")
                
            # Clinical interpretation
            if normalized_score >= 8:
                interpretation = "Excellent balance control"
                feedback = "Outstanding proprioceptive control"
                color = (0, 255, 0)
            elif normalized_score >= 6:
                interpretation = "Good balance with minor instability"
                feedback = "Continue balance training exercises"
                color = (0, 255, 255)
            else:
                interpretation = "Poor balance control - proprioceptive deficit likely"
                feedback = self.feedback_messages['balance_sway']['en']
                color = (0, 0, 255)
                
            return MovementScore(
                raw_angle=sway_area,
                normalized_score=normalized_score,
                asymmetry_penalty=0,
                compensation_flags=compensation_flags,
                clinical_interpretation=interpretation,
                feedback_message=feedback,
                color_code=color
            )
            
        except Exception as e:
            return self._create_error_score(f"Balance assessment error: {e}")
    
    def _calculate_sway_area(self, positions: np.ndarray) -> float:
        """Calculate the area of sway using convex hull"""
        try:
            from scipy.spatial import ConvexHull
            if len(positions) < 3:
                return 0.0
            hull = ConvexHull(positions)
            return hull.volume  # Area in 2D
        except:
            # Fallback to simple bounding box area
            if len(positions) == 0:
                return 0.0
            x_range = np.max(positions[:, 0]) - np.min(positions[:, 0])
            y_range = np.max(positions[:, 1]) - np.min(positions[:, 1])
            return x_range * y_range
    
    def _calculate_sway_velocity(self, positions: np.ndarray) -> float:
        """Calculate average sway velocity"""
        if len(positions) < 2:
            return 0.0
        
        velocities = []
        for i in range(1, len(positions)):
            dist = np.linalg.norm(positions[i] - positions[i-1])
            velocities.append(dist)
            
        return np.mean(velocities) if velocities else 0.0
    
    def _create_error_score(self, error_msg: str) -> MovementScore:
        """Create error score for failed assessments"""
        return MovementScore(
            raw_angle=0,
            normalized_score=0,
            asymmetry_penalty=0,
            compensation_flags=["assessment_error"],
            clinical_interpretation=f"Assessment failed: {error_msg}",
            feedback_message="Unable to assess - check pose visibility",
            color_code=(128, 128, 128)  # Gray
        )
    
    def get_comprehensive_assessment(self, landmarks, age: int) -> Dict[str, MovementScore]:
        """Run all movement quality assessments"""
        assessments = {}
        
        try:
            assessments['neck_flexibility'] = self.assess_neck_flexibility(landmarks, age)
            assessments['hip_extension_right'] = self.assess_hip_extension(landmarks, age, 'right')
            assessments['hip_extension_left'] = self.assess_hip_extension(landmarks, age, 'left')
            assessments['squat_quality'] = self.assess_squat_quality(landmarks, age)
            assessments['balance_quality'] = self.assess_balance_quality(landmarks)
            
        except Exception as e:
            print(f"Error in comprehensive assessment: {e}")
            
        return assessments
    
    def generate_clinical_report(self, assessments: Dict[str, MovementScore], patient_age: int) -> Dict:
        """Generate clinical interpretation report"""
        report = {
            'patient_age': patient_age,
            'assessment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': 0,
            'red_flags': [],
            'interventions': [],
            'detailed_scores': {}
        }
        
        total_score = 0
        valid_assessments = 0
        
        for test_name, score in assessments.items():
            if score.normalized_score > 0:  # Valid assessment
                total_score += score.normalized_score
                valid_assessments += 1
                
                # Add to detailed scores
                report['detailed_scores'][test_name] = {
                    'score': score.normalized_score,
                    'interpretation': score.clinical_interpretation,
                    'compensations': score.compensation_flags
                }
                
                # Check for red flags
                if score.normalized_score < 5:
                    report['red_flags'].append({
                        'test': test_name,
                        'issue': score.clinical_interpretation,
                        'recommendation': score.feedback_message
                    })
        
        # Calculate overall score
        if valid_assessments > 0:
            report['overall_score'] = round(total_score / valid_assessments, 1)
            
        return report
    
    def draw_real_time_feedback(self, frame: np.ndarray, assessments: Dict[str, MovementScore]) -> np.ndarray:
        """Draw real-time feedback overlay on frame"""
        overlay_frame = frame.copy()
        y_offset = 30
        
        for test_name, score in assessments.items():
            if score.normalized_score > 0:  # Valid score
                # Display score with color coding
                text = f"{test_name.replace('_', ' ').title()}: {score.normalized_score:.1f}/10"
                cv2.putText(overlay_frame, text, (30, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, score.color_code, 2)
                y_offset += 30
                
                # Show feedback message if score is low
                if score.normalized_score < 6:
                    feedback_text = score.feedback_message[:50] + "..." if len(score.feedback_message) > 50 else score.feedback_message
                    cv2.putText(overlay_frame, feedback_text, (30, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, score.color_code, 1)
                    y_offset += 25
        
        return overlay_frame

# Usage example integration
def integrate_with_existing_analyzer():
    """Example of how to integrate with existing PoseAnalyzer"""
    pass