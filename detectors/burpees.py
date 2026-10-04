from core.base_exercise import BaseExercise


class BurpeesDetector(BaseExercise):

    HIP_DOWN_THRESHOLD = 100
    HIP_UP_THRESHOLD = 160

    ELBOW_PUSHUP_THRESHOLD = 100

    BODY_ALIGNMENT_THRESHOLD = 160

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

    def reset(self):
        self.reps = 0
        self.stage = "standing"

    def process(self, landmarks):

        # calculate left visibility
        left_visibility = (
            landmarks[self.LEFT_SHOULDER].visibility
            + landmarks[self.LEFT_ELBOW].visibility
            + landmarks[self.LEFT_WRIST].visibility
            + landmarks[self.LEFT_HIP].visibility
            + landmarks[self.LEFT_KNEE].visibility
            + landmarks[self.LEFT_ANKLE].visibility
        ) / 6

        # calculate right visibility
        right_visibility = (
            landmarks[self.RIGHT_SHOULDER].visibility
            + landmarks[self.RIGHT_ELBOW].visibility
            + landmarks[self.RIGHT_WRIST].visibility
            + landmarks[self.RIGHT_HIP].visibility
            + landmarks[self.RIGHT_KNEE].visibility
            + landmarks[self.RIGHT_ANKLE].visibility
        ) / 6

        # choose the side with better visibility
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

        # check if important landmarks are visible
        key_landmarks_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[hip_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY
        )

        if not key_landmarks_visible:
            return {
                "reps": self.reps,
                "hip_angle": 0,
                "elbow_angle": 0,
                "body_alignment": "N/A",
                "composite_movement": "N/A"
            }

        # calculate hip angle
        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )

        # calculate elbow angle
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx)
        )

        # calculate body alignment
        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx)
        )

        # for body_alignment
        if body_angle >= self.BODY_ALIGNMENT_THRESHOLD:
            body_alignment = "Good"
        else:
            body_alignment = "Poor"

        # for composite_movement
        if hip_angle >= self.HIP_UP_THRESHOLD:
            composite_movement = "Standing"

        elif hip_angle < self.HIP_DOWN_THRESHOLD:
            if elbow_angle <= self.ELBOW_PUSHUP_THRESHOLD:
                composite_movement = "Push-up"
            else:
                composite_movement = "Crouching"

        elif body_angle >= self.BODY_ALIGNMENT_THRESHOLD:
            composite_movement = "Plank"

        else:
            composite_movement = "Transition"

        # count burpee reps
        if composite_movement == "Standing":
            if self.stage == "returning":
                self.reps += 1

            self.stage = "standing"

        elif composite_movement == "Crouching":
            if self.stage == "standing":
                self.stage = "crouching"

        elif composite_movement == "Plank":
            if self.stage == "crouching":
                self.stage = "plank"

        elif composite_movement == "Push-up":
            if self.stage == "plank":
                self.stage = "push-up"

        if (
            self.stage == "push-up"
            and composite_movement == "Plank"
        ):
            self.stage = "returning"

        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "elbow_angle": int(elbow_angle),
            "body_alignment": body_alignment,
            "composite_movement": composite_movement
        }