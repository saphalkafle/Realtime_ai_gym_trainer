from core.base_exercise import BaseExercise


class SquatDetector(BaseExercise):

    # Angle thresholds
    SQUAT_DOWN_THRESHOLD = 100
    SQUAT_UP_THRESHOLD = 160

    # Visibility
    MIN_VISIBILITY = 0.7

    # Upper body
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16

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

    def process(self,landmarks):
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks,self.LEFT_HIP),
            self.get_point(landmarks,self.LEFT_KNEE),
            self.get_point(landmarks,self.LEFT_ANKLE),
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks,self.RIGHT_HIP),
            self.get_point(landmarks,self.RIGHT_KNEE),
            self.get_point(landmarks,self.RIGHT_ANKLE),
        )

    