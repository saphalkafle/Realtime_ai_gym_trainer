import os
import cv2
import threading
from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.burpees import BurpeesDetector
from detectors.jumping_jack import JumpingJackDetector
from detectors.leg_raises import LegRaiseDetector
from detectors.lunges import LungesDetector
from detectors.Mountain_climber import MountainClimberDetector
from detectors.plank import PlankDetector
from detectors.pullup import PullupDetector
from detectors.pushup import PushupDetector
from detectors.squat import SquatDetector
from services.config.workout_config import POSE_CONNECTIONS



class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"

        model_path = os.path.join(os.getcwd(),"ml_models","pose_landmarker_full.task")
        base_option = python.BaseOptions(model_path=model_path)

        options = vision.PoseLandmarkerOptions(
            base_option=base_option,
            running_mode= vision.RunningMode.VIDEO,
            min_pose_detection_confidence = 0.7,
            min_pose_presence_confidence = 0.7,
            min_tracking_confidence = 0.7,
            output_segmentation_masks = False
        )


        self._landmarker = vision.PoseLandmarker.create_from_options(options)

        self._detectors = {
            "Squats": SquatDetector(),
            "Push-up": PushupDetector(),
            "Burpees": BurpeesDetector(),
            "Pull-ups": PullupDetector(),
            "Lunges": LungesDetector(),
            "Planks": PlankDetector(),
            "Jumping Jack": JumpingJackDetector(),
            "Mountain climbers": MountainClimberDetector(),
            "Leg-Raises": LegRaiseDetector(),
        }

        self._frame_timestamps_ms = 0

    def set_latest_metrics(self,metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()


    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()


    def set_exercise(self,exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self._exercise_type

    def _draw_skeleton(self,img,landmarks):
        h,w = img.shape[:2]

        for start_idx, end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]


            if p1.visibility > 0.7 and p2.visibility > 0.7:
                cv2.line(
                    img,
                    (int(p1.x * w), int(p1.y*h)), #starting point
                    (int(p2.x * w), int(p2.y*h)), #ending point
                    (255, 255, 0), #color
                    3
                )

        for lm in landmarks:
            if lm.visibility > 0.7:
                cv2.circle(
                    img,
                    (int(lm.x * w),int(lm.y*h)),
                    8,
                    (255,0,225),
                    -1 #thickness
                )

        return img


    #no pose warning
    def _draw_no_pose_warnings(self,img):
        cv2.putText(
            img,
            "No Pose Detected",
            (30,50), #x and y
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            img,
            "Please Face The Camera",
            (30,100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
            cv2.LINE_AA,
        )

    

    