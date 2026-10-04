from core.base_exercise import BaseExercise


class PullupDetector(BaseExercise):

    PULLUP_UP_THRESHOLD = 90
    PULLUP_DOWN_THRESHOLD = 160

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

    SHOULDER_ALIGNMENT_TOLERANCE = 0.08

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = "None"

    def process(self, landmarks):

        # calculate left visibility
        left_visibility = (
            landmarks[self.LEFT_ELBOW].visibility
            + landmarks[self.LEFT_SHOULDER].visibility
            + landmarks[self.LEFT_WRIST].visibility
        ) / 3

        # calculate right visibility
        right_visibility = (
            landmarks[self.RIGHT_ELBOW].visibility
            + landmarks[self.RIGHT_SHOULDER].visibility
            + landmarks[self.RIGHT_WRIST].visibility
        ) / 3

        # choose the side with better visibility
        if left_visibility >= right_visibility:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE

        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE

        # check if important landmarks are visible
        key_landmark_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
        )

        if not key_landmark_visible:
            return {
                "reps": self.reps,
                "elbow_angle": 0,
                "shoulder_status": "N/A",
                "extension_status": "N/A",
                "back_arch_status": "N/A"
            }

        # calculate elbow angle
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx)
        )

        # calculate back angle
        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )

        # count pullup reps
        if elbow_angle <= self.PULLUP_UP_THRESHOLD:
            self.stage = "up"

        elif (
            elbow_angle >= self.PULLUP_DOWN_THRESHOLD
            and self.stage == "up"
        ):
            self.reps += 1
            self.stage = "down"

        # for shoulder_status
        wrist_shoulder_difference = abs(
            landmarks[wrist_idx].y
            - landmarks[shoulder_idx].y
        )

        if wrist_shoulder_difference <= self.SHOULDER_ALIGNMENT_TOLERANCE:
            shoulder_status = "Good"
        else:
            shoulder_status = "Incorrect"

        # for extension_status
        if elbow_angle >= self.PULLUP_DOWN_THRESHOLD:
            extension_status = "Proper"
        else:
            extension_status = "No Proper Extension"

        # for back_arch_status
        if back_angle >= 160:
            back_arch_status = "Neutral"
        elif back_angle >= 140:
            back_arch_status = "Slight Arch"
        else:
            back_arch_status = "Excessive Arch"

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "shoulder_status": shoulder_status,
            "extension_status": extension_status,
            "back_arch_status": back_arch_status
        }