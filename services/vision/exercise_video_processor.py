import os
import threading
from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_matrics = None
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

    