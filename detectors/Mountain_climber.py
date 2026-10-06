from core.base_exercise import BaseExercise
import math


class MountainClimberDetector(BaseExercise):

    # Knee angle (hip-knee-ankle): small = knee pulled in, large = leg straight
    KNEE_UP_THRESHOLD = 100
    KNEE_EXTENDED_THRESHOLD = 140

    # Torso angle from horizontal (degrees). 0 = body flat like a plank.
    MAX_TORSO_ANGLE = 30

    # Lower than plank because the far-side leg is often partly hidden
    MIN_VISIBILITY = 0.5

    # Left side
    LEFT_SHOULDER = 11
    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27

    # Right side
    RIGHT_SHOULDER = 12
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

        # Pick the side the camera sees best (used for torso + hip angle)
        if left_visibility >= right_visibility:
            shoulder_idx = self.LEFT_SHOULDER
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE

        # Both legs are needed to know which knee is up
        key_landmark_visible = all(
            landmarks[idx].visibility >= self.MIN_VISIBILITY
            for idx in (
                shoulder_idx, hip_idx, knee_idx,
                self.LEFT_KNEE, self.RIGHT_KNEE,
                self.LEFT_ANKLE, self.RIGHT_ANKLE,
            )
        )

        if not key_landmark_visible:
            return {
                "knee_angle": 0,
                "hip_angle": 0,
                "torso_angle": 0,
                "composite_movement": "N/A",
            }

        # Knee angle of each leg: hip -> knee -> ankle
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE),
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE),
        )

        # The more bent knee is the active one (the one being driven forward)
        knee_angle = min(left_knee_angle, right_knee_angle)

        # Hip angle: shoulder -> hip -> knee (on the visible side)
        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        # Torso angle: how far the shoulder-hip line is from horizontal
        dx = abs(landmarks[hip_idx].x - landmarks[shoulder_idx].x)
        dy = abs(landmarks[hip_idx].y - landmarks[shoulder_idx].y)
        torso_angle = math.degrees(math.atan2(dy, dx))


        # Which leg is up / extended?
        left_up = left_knee_angle <= self.KNEE_UP_THRESHOLD
        right_up = right_knee_angle <= self.KNEE_UP_THRESHOLD
        left_extended = left_knee_angle >= self.KNEE_EXTENDED_THRESHOLD
        right_extended = right_knee_angle >= self.KNEE_EXTENDED_THRESHOLD


        #Movement
        if torso_angle > self.MAX_TORSO_ANGLE:
            composite_movement = "BAD POSTURE"
        elif left_up and right_extended:
            composite_movement = "LEFT KNEE UP"
        elif right_up and left_extended:
            composite_movement = "RIGHT KNEE UP"
        elif left_extended and right_extended:
            composite_movement = "PLANK"
        else:
            composite_movement = "TRANSITION"

        return {
            "knee_angle": int(knee_angle),
            "hip_angle": int(hip_angle),
            "torso_angle": int(torso_angle),
            "composite_movement": composite_movement,
        }