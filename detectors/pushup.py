from core.base_exercise import BaseExercise

class Pushup(BaseExercise):
    PUSHUP_UP_THRESHOLD = 160
    PUSHUP_DOWN_THRESHOLD = 90

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
        self.reps = 0
        self.stage = "None"

    