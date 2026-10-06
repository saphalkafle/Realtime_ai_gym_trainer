from core.base_exercise import BaseExercise
import math


class LegRaiseDetector(BaseExercise):

    # Hip angle (shoulder-hip-knee): 180 = legs flat, 90 = legs straight up
    LEGRAISE_UP_THRESHOLD = 100     # was 70, which needs legs past vertical
    LEGRAISE_DOWN_THRESHOLD = 150

    # Knee angle (hip-knee-ankle): above this the leg counts as straight
    KNEE_STRAIGHT_THRESHOLD = 150

    MIN_VISIBILITY = 0.7

    # Upper body
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    # Lower body
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

    def process(self, landmarks):

        # Average visibility of each side
        left_visibility = (
            landmarks[self.LEFT_SHOULDER].visibility
            + landmarks[self.LEFT_HIP].visibility
            + landmarks[self.LEFT_KNEE].visibility
            + landmarks[self.LEFT_ANKLE].visibility
        ) / 4

        right_visibility = (
            landmarks[self.RIGHT_SHOULDER].visibility
            + landmarks[self.RIGHT_HIP].visibility
            + landmarks[self.RIGHT_KNEE].visibility
            + landmarks[self.RIGHT_ANKLE].visibility
        ) / 4

        # Use the better-seen side
        if left_visibility >= right_visibility:
            shoulder_idx = self.LEFT_SHOULDER
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
            ankle_idx = self.LEFT_ANKLE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE
            ankle_idx = self.RIGHT_ANKLE

        key_landmark_visible = all(
            landmarks[idx].visibility >= self.MIN_VISIBILITY
            for idx in (shoulder_idx, hip_idx, knee_idx, ankle_idx)
        )

        if not key_landmark_visible:
            return {
                "reps": self.reps,
                "hip_angle": 0,
                "torso_angle": 0,
                "extension_status": "N/A",
            }

        # Hip angle: shoulder -> hip -> knee (how far the legs are lifted)
        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        # Knee angle: hip -> knee -> ankle (are the legs straight?)
        knee_angle = self.calculate_angle(
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
            self.get_point(landmarks, ankle_idx),
        )

        # Torso angle: tilt of the shoulder-hip line from horizontal.
        # 0 = back flat on the floor, bigger = upper body lifting off.
        dx = abs(landmarks[hip_idx].x - landmarks[shoulder_idx].x)
        dy = abs(landmarks[hip_idx].y - landmarks[shoulder_idx].y)
        torso_angle = math.degrees(math.atan2(dy, dx))

        # Leg extension
        if knee_angle >= self.KNEE_STRAIGHT_THRESHOLD:
            extension_status = "EXTENDED"
        else:
            extension_status = "BENT"

        # Rep counting: legs up (and straight), then back down
        if hip_angle < self.LEGRAISE_UP_THRESHOLD and knee_angle >= self.KNEE_STRAIGHT_THRESHOLD:
            self.stage = "up"

        elif hip_angle > self.LEGRAISE_DOWN_THRESHOLD and self.stage == "up":
            self.stage = "down"
            self.reps += 1

        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "torso_angle": int(torso_angle),
            "extension_status": extension_status,
        }