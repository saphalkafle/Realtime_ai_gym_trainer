from core.base_exercise import BaseExercise
import math


class BurpeesDetector(BaseExercise):

    # Hip angle (shoulder-hip-knee)
    HIP_DOWN_THRESHOLD = 100    # below this = crouching
    HIP_UP_THRESHOLD = 160      # above this = standing straight

    # Elbow angle: below this in plank position = push-up bottom
    ELBOW_PUSHUP_THRESHOLD = 100

    # Shoulder-hip-ankle angle: above this = body in a straight line
    BODY_ALIGNMENT_THRESHOLD = 160

    # Shoulder-to-ankle line tilt from horizontal (degrees).
    # Below this the body is lying down (plank / push-up), above = upright.
    HORIZONTAL_TILT_MAX = 35

    # True = a rep only counts if a push-up was done in the plank
    REQUIRE_PUSHUP = False

    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        self.reps = 0
        self.stage = "standing"     # standing -> crouching -> plank -> (back to) standing
        self.pushup_done = False

    def process(self, landmarks):

        # Average visibility of each side
        left_visibility = (
            landmarks[self.LEFT_SHOULDER].visibility
            + landmarks[self.LEFT_ELBOW].visibility
            + landmarks[self.LEFT_WRIST].visibility
            + landmarks[self.LEFT_HIP].visibility
            + landmarks[self.LEFT_KNEE].visibility
            + landmarks[self.LEFT_ANKLE].visibility
        ) / 6

        right_visibility = (
            landmarks[self.RIGHT_SHOULDER].visibility
            + landmarks[self.RIGHT_ELBOW].visibility
            + landmarks[self.RIGHT_WRIST].visibility
            + landmarks[self.RIGHT_HIP].visibility
            + landmarks[self.RIGHT_KNEE].visibility
            + landmarks[self.RIGHT_ANKLE].visibility
        ) / 6

        # Choose the better-seen side
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

        key_landmarks_visible = all(
            landmarks[idx].visibility >= self.MIN_VISIBILITY
            for idx in (shoulder_idx, elbow_idx, wrist_idx, hip_idx, knee_idx, ankle_idx)
        )

        if not key_landmarks_visible:
            return {
                "reps": self.reps,
                "hip_angle": 0,
                "elbow_angle": 0,
                "body_alignment": "N/A",
                "composite_movement": "N/A",
            }

        # Hip angle: shoulder -> hip -> knee
        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        # Elbow angle: shoulder -> elbow -> wrist
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        # Body angle: shoulder -> hip -> ankle (is the body a straight line?)
        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )

        # Is the body lying down? Tilt of the shoulder-ankle line from horizontal.
        # Standing is ~90 degrees, plank / push-up is close to 0.
        dx = abs(landmarks[ankle_idx].x - landmarks[shoulder_idx].x)
        dy = abs(landmarks[ankle_idx].y - landmarks[shoulder_idx].y)
        body_tilt = math.degrees(math.atan2(dy, dx))
        is_horizontal = body_tilt < self.HORIZONTAL_TILT_MAX

        # Movement label.
        # The horizontal check comes FIRST: a plank also has a straight hip
        # angle (~180), so without it a plank would be labelled "Standing".
        if is_horizontal:
            if body_angle >= self.BODY_ALIGNMENT_THRESHOLD:
                if elbow_angle <= self.ELBOW_PUSHUP_THRESHOLD:
                    composite_movement = "Push-up"
                else:
                    composite_movement = "Plank"
            else:
                composite_movement = "Transition"

        elif hip_angle >= self.HIP_UP_THRESHOLD:
            composite_movement = "Standing"

        elif hip_angle < self.HIP_DOWN_THRESHOLD:
            composite_movement = "Crouching"

        else:
            composite_movement = "Transition"

        # Body alignment only matters while lying down
        if is_horizontal:
            body_alignment = "Good" if body_angle >= self.BODY_ALIGNMENT_THRESHOLD else "Poor"
        else:
            body_alignment = "-"

        # Rep counting: standing -> crouching -> plank -> standing = 1 rep
        if composite_movement == "Standing":
            if self.stage == "plank":
                if (not self.REQUIRE_PUSHUP) or self.pushup_done:
                    self.reps += 1
            self.stage = "standing"
            self.pushup_done = False

        elif composite_movement == "Crouching":
            if self.stage == "standing":
                self.stage = "crouching"

        elif composite_movement in ("Plank", "Push-up"):
            if self.stage in ("standing", "crouching"):
                self.stage = "plank"
            if composite_movement == "Push-up" and self.stage == "plank":
                self.pushup_done = True

        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "elbow_angle": int(elbow_angle),
            "body_alignment": body_alignment,
            "composite_movement": composite_movement,
        }