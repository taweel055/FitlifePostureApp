#!/usr/bin/env python3
"""
Complete 6-Test Assessment Protocol
Enhanced movement quality assessment with specific clinical protocols
"""

import numpy as np
import cv2
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

class AssessmentTest(Enum):
    """6 Complete Assessment Tests"""
    NECK_FLEXIBILITY = "neck_flexibility"
    HIP_FLEXIBILITY = "hip_flexibility" 
    CHEST_FLEXIBILITY = "chest_flexibility"
    HAMSTRING_FLEXIBILITY = "hamstring_flexibility"
    FUNCTIONAL_SQUAT = "functional_squat"
    SINGLE_LEG_BALANCE = "single_leg_balance"

@dataclass
class TestResult:
    """Individual test result with clinical context"""
    test_name: str
    raw_measurement: float
    target_value: float
    score: float  # 1-10 scale
    clinical_interpretation: str
    dysfunction_flags: List[str]
    exercise_recommendations: List[str]
    duration: float
    bilateral_comparison: Optional[Dict] = None

class CompleteAssessmentProtocol:
    """
    6-Test Complete Assessment Protocol
    4 minutes total assessment time with real-time analysis
    """
    
    def __init__(self):
        """Initialize complete assessment protocol"""
        self.current_test = None
        self.test_start_time = None
        self.assessment_data = {}
        self.landmark_buffer = []
        
        # Test durations (seconds)
        self.test_durations = {
            AssessmentTest.NECK_FLEXIBILITY: 20,
            AssessmentTest.HIP_FLEXIBILITY: 30,
            AssessmentTest.CHEST_FLEXIBILITY: 20,
            AssessmentTest.HAMSTRING_FLEXIBILITY: 20,
            AssessmentTest.FUNCTIONAL_SQUAT: 45,
            AssessmentTest.SINGLE_LEG_BALANCE: 60  # 30 seconds per leg
        }
        
        # Clinical targets and thresholds
        self.clinical_targets = {
            'neck_flexibility_base': 67.54,
            'neck_flexibility_decline': 0.50,
            'hip_extension_minimum': 20,
            'chest_horizontal_minimum': 35,
            'hamstring_flexibility_minimum': 60,
            'squat_quality_threshold': 7,
            'balance_minimum_duration': 25  # seconds
        }
        
    def calculate_age_adjusted_target(self, base_value: float, decline_rate: float, age: int) -> float:
        """Calculate age-adjusted target values"""
        return base_value - (decline_rate * age)
    
    def start_test(self, test_type: AssessmentTest) -> bool:
        """Start a specific assessment test"""
        self.current_test = test_type
        self.test_start_time = time.time()
        self.landmark_buffer = []
        print(f"🧪 Starting {test_type.value.replace('_', ' ').title()}")
        return True
    
    def assess_neck_flexibility(self, landmarks, age: int) -> TestResult:
        """
        Test 1: Neck Flexibility Assessment (20 seconds)
        Movement: Lateral head tilts left and right
        Target: 67.54° - (0.50 × age)
        """
        try:
            # Get the landmark list from MediaPipe structure
            landmark_list = landmarks.landmark if hasattr(landmarks, 'landmark') else landmarks
            
            # Get key landmarks for neck assessment
            left_ear = np.array([landmark_list[7].x, landmark_list[7].y, landmark_list[7].z])
            nose = np.array([landmark_list[0].x, landmark_list[0].y, landmark_list[0].z])
            right_ear = np.array([landmark_list[8].x, landmark_list[8].y, landmark_list[8].z])
            left_shoulder = np.array([landmark_list[11].x, landmark_list[11].y, landmark_list[11].z])
            right_shoulder = np.array([landmark_list[12].x, landmark_list[12].y, landmark_list[12].z])
            
            # Calculate lateral flexion range
            lateral_tilt = self._calculate_angle_3pts(left_ear, nose, right_ear)
            
            # Calculate forward head posture
            shoulder_midpoint = (left_shoulder + right_shoulder) / 2
            head_forward_angle = self._calculate_angle_3pts(shoulder_midpoint, nose, 
                                                          np.array([nose[0], nose[1] + 0.1, nose[2]]))
            
            # Age-adjusted target
            target_rom = self.calculate_age_adjusted_target(
                self.clinical_targets['neck_flexibility_base'],
                self.clinical_targets['neck_flexibility_decline'],
                age
            )
            
            # Scoring (1-10 scale)
            rom_percentage = (lateral_tilt / target_rom) * 100
            base_score = min(10, max(1, rom_percentage / 10))
            
            # Dysfunction detection
            dysfunction_flags = []
            if lateral_tilt < target_rom * 0.7:
                dysfunction_flags.append("restricted_cervical_rom")
            if head_forward_angle > 15:  # Forward head posture threshold
                dysfunction_flags.append("forward_head_posture")
                base_score -= 1
            if lateral_tilt < target_rom * 0.55:
                dysfunction_flags.append("cervicogenic_headache_risk")
                base_score -= 2
                
            final_score = max(1, min(10, base_score))
            
            # Clinical interpretation
            if final_score >= 8:
                interpretation = "Excellent cervical mobility - no dysfunction detected"
                recommendations = ["Maintain current neck mobility through regular movement"]
            elif final_score >= 6:
                interpretation = "Good cervical mobility with minor restrictions"
                recommendations = ["Daily neck stretches", "Ergonomic workstation assessment"]
            elif final_score >= 4:
                interpretation = "Moderate cervical dysfunction - intervention recommended"
                recommendations = ["Deep neck flexor strengthening", "Upper cervical mobilization", 
                                "Postural correction exercises"]
            else:
                interpretation = "Severe cervical dysfunction - immediate intervention required"
                recommendations = ["Physical therapy referral", "Cervical spine assessment", 
                                "Ergonomic intervention", "Pain management evaluation"]
            
            return TestResult(
                test_name="Neck Flexibility",
                raw_measurement=lateral_tilt,
                target_value=target_rom,
                score=final_score,
                clinical_interpretation=interpretation,
                dysfunction_flags=dysfunction_flags,
                exercise_recommendations=recommendations,
                duration=20.0
            )
            
        except Exception as e:
            return self._create_error_result("Neck Flexibility", str(e))
    
    def assess_hip_flexibility(self, landmarks, age: int) -> TestResult:
        """
        Test 2: Hip Flexibility Assessment (30 seconds)
        Enhanced 90° protocol with backward upper body extension
        Protocol: Turn sideways, bend backward while engaging core
        """
        try:
            # Get the landmark list from MediaPipe structure
            landmark_list = landmarks.landmark if hasattr(landmarks, 'landmark') else landmarks
            
            # Get bilateral hip landmarks
            left_shoulder = np.array([landmark_list[11].x, landmark_list[11].y, landmark_list[11].z])
            right_shoulder = np.array([landmark_list[12].x, landmark_list[12].y, landmark_list[12].z])
            left_hip = np.array([landmark_list[23].x, landmark_list[23].y, landmark_list[23].z])
            right_hip = np.array([landmark_list[24].x, landmark_list[24].y, landmark_list[24].z])
            left_knee = np.array([landmark_list[25].x, landmark_list[25].y, landmark_list[25].z])
            right_knee = np.array([landmark_list[26].x, landmark_list[26].y, landmark_list[26].z])
            
            # Calculate hip extension angles (both sides)
            left_hip_angle = 180 - self._calculate_angle_3pts(left_shoulder, left_hip, left_knee)
            right_hip_angle = 180 - self._calculate_angle_3pts(right_shoulder, right_hip, right_knee)
            
            # Average hip extension
            avg_hip_extension = (left_hip_angle + right_hip_angle) / 2
            
            # Bilateral asymmetry
            asymmetry = abs(left_hip_angle - right_hip_angle)
            
            # Scoring based on hip extension range
            target_extension = self.clinical_targets['hip_extension_minimum']
            extension_score = min(10, max(1, (avg_hip_extension / target_extension) * 5))
            
            # Asymmetry penalty
            asymmetry_penalty = min(3, asymmetry / 5)  # 1 point per 5° asymmetry
            
            final_score = max(1, extension_score - asymmetry_penalty)
            
            # Dysfunction detection
            dysfunction_flags = []
            if avg_hip_extension < 10:
                dysfunction_flags.append("severe_hip_flexor_tightness")
            elif avg_hip_extension < 15:
                dysfunction_flags.append("moderate_hip_flexor_tightness")
            if asymmetry > 10:
                dysfunction_flags.append("bilateral_hip_asymmetry")
            if avg_hip_extension < 5:
                dysfunction_flags.append("lumbar_compensation_risk")
                
            # Clinical interpretation and recommendations
            if final_score >= 8:
                interpretation = "Excellent hip flexibility - optimal range of motion"
                recommendations = ["Maintain current flexibility through regular activity"]
            elif final_score >= 6:
                interpretation = "Good hip flexibility with minor tightness"
                recommendations = ["Hip flexor stretching 2x30s daily", "Glute activation exercises"]
            elif final_score >= 4:
                interpretation = "Moderate hip flexor tightness - affects posture and movement"
                recommendations = ["Half-kneeling hip flexor stretch", "Thomas stretch protocol", 
                                "Core strengthening", "Postural awareness training"]
            else:
                interpretation = "Severe hip flexor restriction - significant movement limitation"
                recommendations = ["Intensive hip flexor stretching program", "Manual therapy", 
                                "Movement pattern retraining", "Ergonomic assessment"]
            
            # Bilateral comparison data
            bilateral_data = {
                'left_hip_extension': left_hip_angle,
                'right_hip_extension': right_hip_angle,
                'asymmetry': asymmetry,
                'dominant_side': 'left' if left_hip_angle > right_hip_angle else 'right'
            }
            
            return TestResult(
                test_name="Hip Flexibility",
                raw_measurement=avg_hip_extension,
                target_value=target_extension,
                score=final_score,
                clinical_interpretation=interpretation,
                dysfunction_flags=dysfunction_flags,
                exercise_recommendations=recommendations,
                duration=30.0,
                bilateral_comparison=bilateral_data
            )
            
        except Exception as e:
            return self._create_error_result("Hip Flexibility", str(e))
    
    def assess_chest_flexibility(self, landmarks, age: int) -> TestResult:
        """
        Test 3: Chest Flexibility Assessment (20 seconds)
        Movement: Bilateral arm backward extension with shoulder blade squeeze
        Measurement: Shoulder horizontal abduction in degrees
        """
        try:
            # Get the landmark list from MediaPipe structure
            landmark_list = landmarks.landmark if hasattr(landmarks, 'landmark') else landmarks
            
            # Get shoulder and arm landmarks
            left_shoulder = np.array([landmark_list[11].x, landmark_list[11].y, landmark_list[11].z])
            right_shoulder = np.array([landmark_list[12].x, landmark_list[12].y, landmark_list[12].z])
            left_elbow = np.array([landmark_list[13].x, landmark_list[13].y, landmark_list[13].z])
            right_elbow = np.array([landmark_list[14].x, landmark_list[14].y, landmark_list[14].z])
            
            # Calculate spine midpoint
            spine_mid = (left_shoulder + right_shoulder) / 2
            
            # Calculate horizontal abduction angles
            left_horizontal_abd = self._calculate_angle_3pts(left_elbow, left_shoulder, spine_mid)
            right_horizontal_abd = self._calculate_angle_3pts(right_elbow, right_shoulder, spine_mid)
            
            # Average horizontal abduction
            avg_horizontal_abd = (left_horizontal_abd + right_horizontal_abd) / 2
            
            # Bilateral asymmetry
            asymmetry = abs(left_horizontal_abd - right_horizontal_abd)
            
            # Scoring
            target_abduction = self.clinical_targets['chest_horizontal_minimum']
            abduction_score = min(10, max(1, (avg_horizontal_abd / target_abduction) * 8))
            
            # Asymmetry penalty
            asymmetry_penalty = min(2, asymmetry / 8)
            
            final_score = max(1, abduction_score - asymmetry_penalty)
            
            # Dysfunction detection
            dysfunction_flags = []
            if avg_horizontal_abd < 25:
                dysfunction_flags.append("severe_pectoral_tightness")
            elif avg_horizontal_abd < 30:
                dysfunction_flags.append("moderate_pectoral_tightness")
            if asymmetry > 15:
                dysfunction_flags.append("shoulder_asymmetry")
            if avg_horizontal_abd < 20:
                dysfunction_flags.append("rounded_shoulder_posture")
                
            # Clinical interpretation
            if final_score >= 8:
                interpretation = "Excellent chest flexibility - optimal postural health"
                recommendations = ["Maintain through regular stretching and strengthening"]
            elif final_score >= 6:
                interpretation = "Good chest flexibility with minor tightness"
                recommendations = ["Daily doorway chest stretches", "Thoracic extension exercises"]
            elif final_score >= 4:
                interpretation = "Moderate chest tightness - common in desk workers"
                recommendations = ["Pectoral stretching protocol", "Thoracic spine mobility", 
                                "Posterior chain strengthening", "Ergonomic workstation setup"]
            else:
                interpretation = "Severe chest tightness - significant postural dysfunction"
                recommendations = ["Intensive chest stretching program", "Manual therapy", 
                                "Postural correction exercises", "Ergonomic intervention"]
            
            bilateral_data = {
                'left_horizontal_abduction': left_horizontal_abd,
                'right_horizontal_abduction': right_horizontal_abd,
                'asymmetry': asymmetry
            }
            
            return TestResult(
                test_name="Chest Flexibility",
                raw_measurement=avg_horizontal_abd,
                target_value=target_abduction,
                score=final_score,
                clinical_interpretation=interpretation,
                dysfunction_flags=dysfunction_flags,
                exercise_recommendations=recommendations,
                duration=20.0,
                bilateral_comparison=bilateral_data
            )
            
        except Exception as e:
            return self._create_error_result("Chest Flexibility", str(e))
    
    def assess_hamstring_flexibility(self, landmarks, age: int) -> TestResult:
        """
        Test 4: Hamstring Flexibility Assessment (20 seconds)
        Movement: Forward bend with optional toe dorsiflexion
        Safety: Maintains slight knee bend to prevent hyperextension
        """
        try:
            # Get the landmark list from MediaPipe structure
            landmark_list = landmarks.landmark if hasattr(landmarks, 'landmark') else landmarks
            
            # Get key landmarks for hamstring assessment
            left_hip = np.array([landmark_list[23].x, landmark_list[23].y, landmark_list[23].z])
            right_hip = np.array([landmark_list[24].x, landmark_list[24].y, landmark_list[24].z])
            left_knee = np.array([landmark_list[25].x, landmark_list[25].y, landmark_list[25].z])
            right_knee = np.array([landmark_list[26].x, landmark_list[26].y, landmark_list[26].z])
            left_ankle = np.array([landmark_list[27].x, landmark_list[27].y, landmark_list[27].z])
            right_ankle = np.array([landmark_list[28].x, landmark_list[28].y, landmark_list[28].z])
            
            # Calculate hip flexion angles (hamstring length indicator)
            left_hip_flexion = self._calculate_angle_3pts(left_knee, left_hip, 
                                                        np.array([left_hip[0], left_hip[1] + 0.1, left_hip[2]]))
            right_hip_flexion = self._calculate_angle_3pts(right_knee, right_hip,
                                                         np.array([right_hip[0], right_hip[1] + 0.1, right_hip[2]]))
            
            # Average hip flexion
            avg_hip_flexion = (left_hip_flexion + right_hip_flexion) / 2
            
            # Check knee safety (should maintain slight bend)
            left_knee_angle = self._calculate_angle_3pts(left_hip, left_knee, left_ankle)
            right_knee_angle = self._calculate_angle_3pts(right_hip, right_knee, right_ankle)
            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
            
            # Safety check - penalize hyperextension
            safety_penalty = 0
            if avg_knee_angle > 185:  # Hyperextension
                safety_penalty = 2
                
            # Bilateral asymmetry
            asymmetry = abs(left_hip_flexion - right_hip_flexion)
            
            # Scoring
            target_flexion = self.clinical_targets['hamstring_flexibility_minimum']
            flexion_score = min(10, max(1, (avg_hip_flexion / target_flexion) * 8))
            
            # Penalties
            asymmetry_penalty = min(2, asymmetry / 10)
            
            final_score = max(1, flexion_score - asymmetry_penalty - safety_penalty)
            
            # Dysfunction detection
            dysfunction_flags = []
            if avg_hip_flexion < 45:
                dysfunction_flags.append("severe_hamstring_tightness")
            elif avg_hip_flexion < 55:
                dysfunction_flags.append("moderate_hamstring_tightness")
            if asymmetry > 15:
                dysfunction_flags.append("bilateral_hamstring_asymmetry")
            if avg_knee_angle > 185:
                dysfunction_flags.append("knee_hyperextension_risk")
            if avg_hip_flexion < 40:
                dysfunction_flags.append("lower_back_compensation_risk")
                
            # Clinical interpretation
            if final_score >= 8:
                interpretation = "Excellent hamstring flexibility - optimal posterior chain"
                recommendations = ["Maintain flexibility through regular activity"]
            elif final_score >= 6:
                interpretation = "Good hamstring flexibility with minor tightness"
                recommendations = ["Regular hamstring stretching", "Dynamic warm-up routine"]
            elif final_score >= 4:
                interpretation = "Moderate hamstring tightness - affects movement quality"
                recommendations = ["PNF hamstring stretching", "RDL movement pattern training", 
                                "Hip hinge education", "Dynamic stretching routine"]
            else:
                interpretation = "Severe hamstring restriction - significant movement limitation"
                recommendations = ["Intensive hamstring stretching program", "Manual therapy", 
                                "Movement pattern retraining", "Gradual flexibility progression"]
            
            bilateral_data = {
                'left_hip_flexion': left_hip_flexion,
                'right_hip_flexion': right_hip_flexion,
                'asymmetry': asymmetry,
                'knee_safety_score': 10 - safety_penalty
            }
            
            return TestResult(
                test_name="Hamstring Flexibility",
                raw_measurement=avg_hip_flexion,
                target_value=target_flexion,
                score=final_score,
                clinical_interpretation=interpretation,
                dysfunction_flags=dysfunction_flags,
                exercise_recommendations=recommendations,
                duration=20.0,
                bilateral_comparison=bilateral_data
            )
            
        except Exception as e:
            return self._create_error_result("Hamstring Flexibility", str(e))
    
    def assess_functional_squat(self, landmarks, age: int) -> TestResult:
        """
        Test 5: Functional Squat Assessment (45 seconds)
        Movement: 3-5 controlled squat repetitions
        Analysis: Multi-joint coordination, ankle/knee/hip mobility
        Output: 1-10 movement quality score with dysfunction identification
        """
        try:
            # Get the landmark list from MediaPipe structure
            landmark_list = landmarks.landmark if hasattr(landmarks, 'landmark') else landmarks
            
            # Get bilateral landmarks for squat analysis
            left_hip = np.array([landmark_list[23].x, landmark_list[23].y, landmark_list[23].z])
            right_hip = np.array([landmark_list[24].x, landmark_list[24].y, landmark_list[24].z])
            left_knee = np.array([landmark_list[25].x, landmark_list[25].y, landmark_list[25].z])
            right_knee = np.array([landmark_list[26].x, landmark_list[26].y, landmark_list[26].z])
            left_ankle = np.array([landmark_list[27].x, landmark_list[27].y, landmark_list[27].z])
            right_ankle = np.array([landmark_list[28].x, landmark_list[28].y, landmark_list[28].z])
            
            # Calculate key squat angles
            left_knee_angle = self._calculate_angle_3pts(left_hip, left_knee, left_ankle)
            right_knee_angle = self._calculate_angle_3pts(right_hip, right_knee, right_ankle)
            
            # Hip angles
            left_hip_angle = self._calculate_angle_3pts(
                np.array([left_hip[0], left_hip[1] + 0.1, left_hip[2]]), left_hip, left_knee)
            right_hip_angle = self._calculate_angle_3pts(
                np.array([right_hip[0], right_hip[1] + 0.1, right_hip[2]]), right_hip, right_knee)
            
            # Knee tracking assessment (valgus/varus)
            knee_separation = abs(left_knee[0] - right_knee[0])
            hip_separation = abs(left_hip[0] - right_hip[0])
            knee_tracking_ratio = knee_separation / hip_separation if hip_separation > 0 else 1
            
            # Depth assessment
            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
            squat_depth_score = min(10, max(1, (180 - avg_knee_angle) / 9))  # 90° = full depth
            
            # Symmetry assessment
            knee_symmetry = 10 - min(5, abs(left_knee_angle - right_knee_angle) / 2)
            hip_symmetry = 10 - min(5, abs(left_hip_angle - right_hip_angle) / 2)
            
            # Knee tracking score
            tracking_score = 10
            if knee_tracking_ratio < 0.7:  # Knee valgus
                tracking_score -= 4
            elif knee_tracking_ratio < 0.8:
                tracking_score -= 2
            
            # Composite squat quality score
            composite_score = (squat_depth_score * 0.4 + 
                             knee_symmetry * 0.2 + 
                             hip_symmetry * 0.2 + 
                             tracking_score * 0.2)
            
            final_score = max(1, min(10, composite_score))
            
            # Dysfunction detection
            dysfunction_flags = []
            if knee_tracking_ratio < 0.7:
                dysfunction_flags.append("knee_valgus_collapse")
            if avg_knee_angle > 135:  # Poor depth
                dysfunction_flags.append("limited_squat_depth")
            if abs(left_knee_angle - right_knee_angle) > 15:
                dysfunction_flags.append("asymmetric_squat_pattern")
            if knee_tracking_ratio > 1.3:
                dysfunction_flags.append("knee_varus_deviation")
            if final_score < 4:
                dysfunction_flags.append("multi_joint_dysfunction")
                
            # Clinical interpretation
            if final_score >= 8:
                interpretation = "Excellent squat mechanics - optimal movement quality"
                recommendations = ["Maintain current movement patterns", "Progress to loaded squats"]
            elif final_score >= 6:
                interpretation = "Good squat quality with minor compensations"
                recommendations = ["Squat mobility routine", "Glute activation exercises", 
                                "Ankle mobility work"]
            elif final_score >= 4:
                interpretation = "Moderate squat dysfunction - corrective approach needed"
                recommendations = ["Corrective squat progression", "Hip and ankle mobility", 
                                "Core stability training", "Movement pattern retraining"]
            else:
                interpretation = "Poor squat mechanics - comprehensive intervention required"
                recommendations = ["Fundamental movement screen", "Individual joint mobility", 
                                "Corrective exercise program", "Professional movement assessment"]
            
            bilateral_data = {
                'left_knee_angle': left_knee_angle,
                'right_knee_angle': right_knee_angle,
                'knee_tracking_ratio': knee_tracking_ratio,
                'squat_depth': 180 - avg_knee_angle,
                'symmetry_score': (knee_symmetry + hip_symmetry) / 2
            }
            
            return TestResult(
                test_name="Functional Squat",
                raw_measurement=final_score,
                target_value=self.clinical_targets['squat_quality_threshold'],
                score=final_score,
                clinical_interpretation=interpretation,
                dysfunction_flags=dysfunction_flags,
                exercise_recommendations=recommendations,
                duration=45.0,
                bilateral_comparison=bilateral_data
            )
            
        except Exception as e:
            return self._create_error_result("Functional Squat", str(e))
    
    def assess_single_leg_balance(self, landmarks, age: int) -> TestResult:
        """
        Test 6: Single-Leg Balance Assessment (30 seconds per leg)
        Movement: Unilateral standing balance hold
        Analysis: Proprioceptive control, stability strategies
        """
        try:
            # Get the landmark list from MediaPipe structure
            landmark_list = landmarks.landmark if hasattr(landmarks, 'landmark') else landmarks
            
            # Track ankle and pelvis landmarks for sway analysis
            left_ankle = np.array([landmark_list[27].x, landmark_list[27].y])
            right_ankle = np.array([landmark_list[28].x, landmark_list[28].y])
            pelvis_center = np.array([
                (landmark_list[23].x + landmark_list[24].x) / 2,
                (landmark_list[23].y + landmark_list[24].y) / 2
            ])
            
            # Add current frame to buffer
            current_time = time.time()
            self.landmark_buffer.append({
                'timestamp': current_time,
                'pelvis': pelvis_center,
                'left_ankle': left_ankle,
                'right_ankle': right_ankle
            })
            
            # Keep only recent data (last 60 seconds)
            self.landmark_buffer = [
                frame for frame in self.landmark_buffer 
                if current_time - frame['timestamp'] <= 60
            ]
            
            if len(self.landmark_buffer) < 30:  # Need minimum data
                return TestResult(
                    test_name="Single-Leg Balance",
                    raw_measurement=0,
                    target_value=self.clinical_targets['balance_minimum_duration'],
                    score=1,
                    clinical_interpretation="Insufficient data - continue holding position",
                    dysfunction_flags=[],
                    exercise_recommendations=["Hold position longer for assessment"],
                    duration=0
                )
            
            # Calculate balance metrics
            pelvis_positions = np.array([frame['pelvis'] for frame in self.landmark_buffer])
            
            # Sway area calculation
            sway_area = self._calculate_sway_area(pelvis_positions)
            
            # Sway velocity
            sway_velocity = self._calculate_sway_velocity(pelvis_positions)
            
            # Balance duration
            balance_duration = len(self.landmark_buffer) / 30  # Assuming 30 FPS
            
            # Scoring components
            duration_score = min(10, (balance_duration / 30) * 10)  # 30s target per leg
            stability_score = max(1, 10 - (sway_area * 5))  # Penalty for excessive sway
            control_score = max(1, 10 - (sway_velocity * 3))  # Penalty for rapid movements
            
            # Composite balance score
            composite_score = (duration_score * 0.5 + stability_score * 0.3 + control_score * 0.2)
            final_score = max(1, min(10, composite_score))
            
            # Dysfunction detection
            dysfunction_flags = []
            if balance_duration < 15:
                dysfunction_flags.append("poor_balance_endurance")
            if sway_area > 3.0:
                dysfunction_flags.append("excessive_postural_sway")
            if sway_velocity > 2.0:
                dysfunction_flags.append("poor_balance_control")
            if balance_duration < 10:
                dysfunction_flags.append("fall_risk_indicator")
            if final_score < 4:
                dysfunction_flags.append("significant_proprioceptive_deficit")
                
            # Clinical interpretation
            if final_score >= 8:
                interpretation = "Excellent balance control - optimal proprioceptive function"
                recommendations = ["Maintain through regular activity", "Progress to dynamic balance"]
            elif final_score >= 6:
                interpretation = "Good balance with minor instability"
                recommendations = ["Single-leg balance training", "Proprioceptive exercises", 
                                "Core strengthening"]
            elif final_score >= 4:
                interpretation = "Moderate balance dysfunction - intervention recommended"
                recommendations = ["Progressive balance training", "Ankle strengthening", 
                                "Proprioceptive rehabilitation", "Fall prevention program"]
            else:
                interpretation = "Poor balance control - significant fall risk"
                recommendations = ["Comprehensive balance assessment", "Physical therapy referral", 
                                "Fall prevention program", "Environmental safety assessment"]
            
            return TestResult(
                test_name="Single-Leg Balance",
                raw_measurement=balance_duration,
                target_value=self.clinical_targets['balance_minimum_duration'],
                score=final_score,
                clinical_interpretation=interpretation,
                dysfunction_flags=dysfunction_flags,
                exercise_recommendations=recommendations,
                duration=balance_duration
            )
            
        except Exception as e:
            return self._create_error_result("Single-Leg Balance", str(e))
    
    def run_complete_assessment(self, landmarks, age: int) -> Dict[str, TestResult]:
        """Run all 6 assessment tests"""
        results = {}
        
        try:
            # Flexibility Tests (2 minutes total)
            results['neck_flexibility'] = self.assess_neck_flexibility(landmarks, age)
            results['hip_flexibility'] = self.assess_hip_flexibility(landmarks, age)
            results['chest_flexibility'] = self.assess_chest_flexibility(landmarks, age)
            results['hamstring_flexibility'] = self.assess_hamstring_flexibility(landmarks, age)
            
            # Movement Quality Tests (2 minutes total)
            results['functional_squat'] = self.assess_functional_squat(landmarks, age)
            results['single_leg_balance'] = self.assess_single_leg_balance(landmarks, age)
            
        except Exception as e:
            print(f"Error in complete assessment: {e}")
            
        return results
    
    def generate_comprehensive_report(self, results: Dict[str, TestResult], age: int) -> Dict:
        """Generate comprehensive clinical report"""
        report = {
            'assessment_protocol': '6-Test Complete Assessment',
            'total_duration': '4 minutes',
            'patient_age': age,
            'assessment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': 0,
            'flexibility_score': 0,
            'movement_quality_score': 0,
            'red_flags': [],
            'priority_interventions': [],
            'exercise_program': [],
            'test_results': {}
        }
        
        flexibility_tests = ['neck_flexibility', 'hip_flexibility', 'chest_flexibility', 'hamstring_flexibility']
        movement_tests = ['functional_squat', 'single_leg_balance']
        
        # Calculate category scores
        flexibility_scores = [results[test].score for test in flexibility_tests if test in results]
        movement_scores = [results[test].score for test in movement_tests if test in results]
        
        if flexibility_scores:
            report['flexibility_score'] = round(sum(flexibility_scores) / len(flexibility_scores), 1)
        if movement_scores:
            report['movement_quality_score'] = round(sum(movement_scores) / len(movement_scores), 1)
        
        # Overall score
        all_scores = flexibility_scores + movement_scores
        if all_scores:
            report['overall_score'] = round(sum(all_scores) / len(all_scores), 1)
        
        # Collect red flags and interventions
        for test_name, result in results.items():
            report['test_results'][test_name] = {
                'score': result.score,
                'measurement': result.raw_measurement,
                'target': result.target_value,
                'interpretation': result.clinical_interpretation,
                'dysfunctions': result.dysfunction_flags
            }
            
            # Red flags (scores < 4)
            if result.score < 4:
                report['red_flags'].append({
                    'test': test_name,
                    'score': result.score,
                    'issue': result.clinical_interpretation,
                    'dysfunctions': result.dysfunction_flags
                })
            
            # Priority interventions
            if result.exercise_recommendations:
                report['priority_interventions'].extend(result.exercise_recommendations[:2])
                report['exercise_program'].extend(result.exercise_recommendations)
        
        # Remove duplicates
        report['priority_interventions'] = list(set(report['priority_interventions']))
        report['exercise_program'] = list(set(report['exercise_program']))
        
        return report
    
    def _calculate_angle_3pts(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        """Calculate angle ABC in degrees"""
        ba, bc = a - b, c - b
        norm_ba, norm_bc = np.linalg.norm(ba), np.linalg.norm(bc)
        if norm_ba == 0 or norm_bc == 0:
            return 0.0
        cosang = np.dot(ba, bc) / (norm_ba * norm_bc)
        cosang = np.clip(cosang, -1.0, 1.0)
        return np.degrees(np.arccos(cosang))
    
    def _calculate_sway_area(self, positions: np.ndarray) -> float:
        """Calculate sway area"""
        if len(positions) < 3:
            return 0.0
        x_range = np.max(positions[:, 0]) - np.min(positions[:, 0])
        y_range = np.max(positions[:, 1]) - np.min(positions[:, 1])
        return x_range * y_range * 1000  # Convert to reasonable scale
    
    def _calculate_sway_velocity(self, positions: np.ndarray) -> float:
        """Calculate average sway velocity"""
        if len(positions) < 2:
            return 0.0
        velocities = [np.linalg.norm(positions[i] - positions[i-1]) 
                     for i in range(1, len(positions))]
        return np.mean(velocities) * 100 if velocities else 0.0  # Scale for readability
    
    def _create_error_result(self, test_name: str, error_msg: str) -> TestResult:
        """Create error result for failed assessments"""
        return TestResult(
            test_name=test_name,
            raw_measurement=0,
            target_value=0,
            score=1,
            clinical_interpretation=f"Assessment error: {error_msg}",
            dysfunction_flags=["assessment_error"],
            exercise_recommendations=["Retry assessment with proper pose visibility"],
            duration=0
        )