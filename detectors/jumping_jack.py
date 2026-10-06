from core.base_exercise import BaseExercise
import math


class JumpingJackDetector(BaseExercise):

    # Arm angle thresholds
    ARM_UP_THRESHOLD = 160
    ARM_DOWN_THRESHOLD = 60

    # Leg separation thresholds (ankle distance / hip width)
    LEG_OPEN_THRESHOLD = 1.8
    LEG_CLOSED_THRESHOLD = 1.1

    # Visibility
    MIN_VISIBILITY = 0.7

    # Upper body
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_WRIST = 15
    RIGHT_WRIST = 16

    # Lower body
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()

    def reset(self):
        pass  # time-based exercise: nothing to reset

    def process(self, landmarks):

        # Pick the side with better shoulder visibility
        if landmarks[self.LEFT_SHOULDER].visibility >= landmarks[self.RIGHT_SHOULDER].visibility:
            shoulder_idx = self.LEFT_SHOULDER
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP

        key_landmark_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[hip_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[self.LEFT_HIP].visibility >= self.MIN_VISIBILITY
            and landmarks[self.RIGHT_HIP].visibility >= self.MIN_VISIBILITY
            and landmarks[self.LEFT_ANKLE].visibility >= self.MIN_VISIBILITY
            and landmarks[self.RIGHT_ANKLE].visibility >= self.MIN_VISIBILITY
        )

        if not key_landmark_visible:
            return {
                "shoulder_angle": 0,
                "swing_status": "N/A",
                "composite_movement": "N/A",
            }

        # Arm angle
        shoulder_angle = self.calculate_angle(
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, wrist_idx),
        )

        # Ankle distance
        ankle_dx = landmarks[self.LEFT_ANKLE].x - landmarks[self.RIGHT_ANKLE].x
        ankle_dy = landmarks[self.LEFT_ANKLE].y - landmarks[self.RIGHT_ANKLE].y
        ankle_distance = math.sqrt(ankle_dx ** 2 + ankle_dy ** 2)

        # Hip distance
        hip_dx = landmarks[self.LEFT_HIP].x - landmarks[self.RIGHT_HIP].x
        hip_dy = landmarks[self.LEFT_HIP].y - landmarks[self.RIGHT_HIP].y
        hip_distance = math.sqrt(hip_dx ** 2 + hip_dy ** 2)

        leg_ratio = ankle_distance / hip_distance if hip_distance > 0 else 0

        # Arms
        if shoulder_angle >= self.ARM_UP_THRESHOLD:
            swing_status = "UP"
        elif shoulder_angle <= self.ARM_DOWN_THRESHOLD:
            swing_status = "DOWN"
        else:
            swing_status = "MID"

        # Legs
        if leg_ratio >= self.LEG_OPEN_THRESHOLD:
            legs_open = True
        elif leg_ratio <= self.LEG_CLOSED_THRESHOLD:
            legs_open = False
        else:
            legs_open = None

        # Full movement
        if swing_status == "UP" and legs_open is True:
            composite_movement = "OPEN"
        elif swing_status == "DOWN" and legs_open is False:
            composite_movement = "CLOSED"
        else:
            composite_movement = "INCOMPLETE"

        return {
            "shoulder_angle": int(shoulder_angle),
            "swing_status": swing_status,
            "composite_movement": composite_movement,
        }