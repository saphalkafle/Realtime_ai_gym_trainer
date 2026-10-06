from core.base_exercise import BaseExercise


class PlankDetector(BaseExercise):

    # Body line angle (shoulder-hip-ankle). 180 = perfectly straight.
    STRAIGHT_THRESHOLD = 160
    SLIGHT_BEND_THRESHOLD = 150

    MIN_VISIBILITY = 0.7
    HIP_SAG_TOLERANCE = 0.08

    # Left side
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27

    # Right side
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()

    def reset(self):
        pass  # time-based exercise: nothing to reset

    def process(self, landmarks):
        left_visibility = landmarks[self.LEFT_SHOULDER].visibility
        right_visibility = landmarks[self.RIGHT_SHOULDER].visibility

        if left_visibility >= right_visibility:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
            ankle_idx = self.LEFT_ANKLE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE
            ankle_idx = self.RIGHT_ANKLE

        key_landmark_visible = all(
            landmarks[idx].visibility >= self.MIN_VISIBILITY
            for idx in (shoulder_idx, elbow_idx, wrist_idx, hip_idx, knee_idx, ankle_idx)
        )

        if not key_landmark_visible:
            return {
                "back_angle": 0,
                "hip_angle": 0,
                "body_alignment": "N/A",
            }

        # Back angle: shoulder -> hip -> ankle (whole body line)
        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )

        # Hip angle: shoulder -> hip -> knee
        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        # Hip position vs the shoulder-ankle line (y grows downward)
        expected_hip_y = (landmarks[shoulder_idx].y + landmarks[ankle_idx].y) / 2
        current_hip_position = landmarks[hip_idx].y - expected_hip_y

        if back_angle >= self.STRAIGHT_THRESHOLD:
            body_alignment = "Straight"
        elif back_angle >= self.SLIGHT_BEND_THRESHOLD:
            body_alignment = "Slightly Bent"
        else:
            body_alignment = "Poor Form"

        # When form is not straight, say which way it is off
        if body_alignment != "Straight":
            if current_hip_position > self.HIP_SAG_TOLERANCE:
                body_alignment += " (Hips Sagging)"
            elif current_hip_position < -self.HIP_SAG_TOLERANCE:
                body_alignment += " (Hips Raised)"

        return {
            "back_angle": int(back_angle),
            "hip_angle": int(hip_angle),
            "body_alignment": body_alignment,
        }