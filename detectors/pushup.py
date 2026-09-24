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

    def process(self,landmarks):
        
        left_visibility = landmarks[self.LEFT_ELBOW].visibility
        right_visibility = landmarks[self.RIGHT_ELBOW].visibility

        if left_visibility >= right_visibility :
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRITST
            hip_idx = self.LEFT_HIP
            ankle_idx = self.LEFT_ANKLE

        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRITST
            hip_idx = self.RIGHT_HIP
            ankle_idx = self.RIGHT_ANKLE

        elbow_angle = self.calculate_angle(
            self.get_point(landmarks,shoulder_idx),
            self.get_point(landmarks,elbow_idx),
            self.get_point(landmarks,wrist_idx)
        )

        body_angle = self.calculate_angle(
            self.get_point(landmarks,shoulder_idx),
            self.get_point(landmarks,hip_idx),
            self.get_point(landmarks,ankle_idx)
        )

        shoulder_y = landmarks[shoulder_idx].y #while pushup y and x axis is taken
        ankle_y = landmarks[ankle_idx].y
        hip_y = landmarks[hip_idx].y

        expected_hip_y = (shoulder_y + ankle_y)/2
        current_hip_position = hip_y - expected_hip_y  #hip deviation


        key_landmark_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY )

        if key_landmark_visible:
            if elbow_angle < self.PUSHUP_DOWN_THRESHOLD:
                self.stage = "down"

            if elbow_angle > self.PUSHUP_up_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        if body_angle > 160:
            body_alignment = "Straight" 
        elif body_angle > 140 :
            body_alignment = "SLightly Bend"
        else:
            body_alignment = "Poor Form"

        if abs(current_hip_position) <= self.HIP_SAG_TOLERANCE:
            hip_status = "Level"
        elif current_hip_position > self.HIP_SAG_TOLERANCE:
            hip_status = "Sagging"
        else:
            hip_status = "Picked up"
            

        return{
            "reps" : self.reps,
            "elbow_angle" : int(elbow_angle),
            "hip_status" : hip_status,
            "body_alignment" : body_alignment

        }

            
