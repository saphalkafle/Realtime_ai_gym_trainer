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



    