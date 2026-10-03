from core.base_exercise import BaseExercise


class LegRaiseDetector(BaseExercise):

    # Hip angle thresholds
    LEGRAISE_UP_THRESHOLD = 70
    LEGRAISE_DOWN_THRESHOLD = 150

    # Knee extension
    KNEE_STRAIGHT_THRESHOLD = 150

    # Visibility
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

     
        #  Calculate visibility of both sides

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

      
        # Select the more visible side
        

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

        # Check landmark visibility
       

        key_landmark_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[hip_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY
        )

        if not key_landmark_visible:
            return {
                "reps": self.reps,
                "hip_angle": 0,
                "torso_angle": 0,
                "extension_status": "N/A"
            }



        hip_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )


        knee_angle = self.calculate_angle(
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
            self.get_point(landmarks, ankle_idx)
        )

        
        # Calculate torso angle

        torso_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )

        
        # Check leg extension
        if knee_angle >= self.KNEE_STRAIGHT_THRESHOLD:
            extension_status = "EXTENDED"
        else:
            extension_status = "BENT"

        
        # Rep detection
        if knee_angle >= self.KNEE_STRAIGHT_THRESHOLD:

            if hip_angle < self.LEGRAISE_UP_THRESHOLD:
                self.stage = "up"

            elif (
                hip_angle > self.LEGRAISE_DOWN_THRESHOLD
                and self.stage == "up"
            ):
                self.stage = "down"
                self.reps += 1

       
        #  Return metrics to main.py
        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "torso_angle": int(torso_angle),
            "extension_status": extension_status
        }