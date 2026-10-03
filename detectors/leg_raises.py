from core.base_exercise import BaseExercise

class LegRaiseDetector(BaseExercise):
    LEGRAISE_UP_THRESHOLD = 
    LEGRAISE_DOWN_THRESHOLD =

    MIN_VISIBILITY = 0.7

    LEFT_HIP =
    RIGHT_HIP = 
    LEFT_ANKLE = 
    RIGHT_ANKLE = 
    LEFT_KNEE =
    RIGHT_KNEE =

    LEFT_SHOULDER =
    RIGHT_SHOULDER =


    def __init__(self):
        super().__init__():

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
        left_visibility = landmarks[self.LEFT_KNEE].visibility
        right_visibility = landmarks[self.RIGHT_KNEE].visibility

        if left_visibility > right_visibility:
            knee_angle = left_knee_angle
            shoulder_idx = self.LEFT_SHOULDER
            hip_idx = self.LEFT_HIP
            ankle_idx = self.LEFT_ANKLE
            knee_idx = self.LEFT_KNEE

        else:
            knee_angle = right_knee_angle
            shoulder_idx = self.RIGHT_SHOULDER
            hip_idx = self.RIGHT_HIP
            ankle_idx = self.RIGHT_ANKLE
            knee_idx = self.RIGHT_KNEE

        

        



