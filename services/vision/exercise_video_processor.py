import os
import cv2
import numpy as np
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

        model_path = os.path.join(os.getcwd(), "ml_models", "pose_landmarker_full.task")
        base_option = python.BaseOptions(model_asset_path=model_path)

        options = vision.PoseLandmarkerOptions(
            base_options=base_option,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            output_segmentation_masks=False,
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

    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()

    def set_exercise(self, exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self._exercise_type

    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]

        for start_idx, end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]

            if p1.visibility > 0.7 and p2.visibility > 0.7:
                cv2.line(
                    img,
                    (int(p1.x * w), int(p1.y * h)),  # starting point
                    (int(p2.x * w), int(p2.y * h)),  # ending point
                    (255, 255, 0),  # color
                    3,
                )

        for lm in landmarks:
            if lm.visibility > 0.7:
                cv2.circle(
                    img,
                    (int(lm.x * w), int(lm.y * h)),
                    8,
                    (255, 0, 225),
                    -1,  # thickness (-1 = filled)
                )

        return img

    # no pose warning
    def _draw_no_pose_warnings(self, img):
        cv2.putText(
            img,
            "No Pose Detected",
            (30, 50),  # x and y
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            img,
            "Please Face The Camera",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    # ------------------------------------------------------------------
    # overlay helpers
    # ------------------------------------------------------------------
    def _fmt(self, metrics, key, angle=False):
        """Safely read a metric. Returns 'N/A' if missing; adds ° for angles."""
        value = metrics.get(key)
        if value is None:
            return "N/A"
        if angle:
            try:
                return f"{float(value):.0f}°"
            except (TypeError, ValueError):
                return str(value)
        return str(value)

    def _put_status(self, img, text, line=0):
        """Draw one line of text at the bottom-left. line=0 is the lowest line;
        higher numbers stack upward so lines never overlap."""
        h, _ = img.shape[:2]
        y = h - 20 - line * 32
        cv2.putText(
            img,
            text,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    
    # overlay dispatcher

    def _draw_overlays(self, img, metrics, ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img, metrics)

        elif ex_type == "Push-up":
            self._draw_pushup_overlays(img, metrics)

        elif ex_type == "Burpees":
            self._draw_burpees_overlays(img, metrics)

        elif ex_type == "Pull-ups":
            self._draw_pullup_overlays(img, metrics)

        elif ex_type == "Lunges":
            self._draw_lunge_overlays(img, metrics)

        elif ex_type == "Planks":
            self._draw_plank_overlays(img, metrics)

        elif ex_type == "Jumping Jack":
            self._draw_jumping_jack_overlays(img, metrics)

        elif ex_type == "Mountain climbers":
            self._draw_mountain_climber_overlays(img, metrics)

        elif ex_type == "Leg-Raises":
            self._draw_leg_raise_overlays(img, metrics)

    # ------------------------------------------------------------------
    # per-exercise overlays
    # ------------------------------------------------------------------
    def _draw_squats_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"KNEE: {f(metrics, 'knee_angle', True)} | BACK: {f(metrics, 'back_angle', True)}", 1)
        self._put_status(img, f"DEPTH: {f(metrics, 'depth_status')}", 0)

    def _draw_pushup_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"ELBOW: {f(metrics, 'elbow_angle', True)} | HIP: {f(metrics, 'hip_status')}", 1)
        self._put_status(img, f"BODY: {f(metrics, 'body_alignment')}", 0)

    def _draw_burpees_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"HIP: {f(metrics, 'hip_angle', True)} | ELBOW: {f(metrics, 'elbow_angle', True)}", 2)
        self._put_status(img, f"BODY: {f(metrics, 'body_alignment')}", 1)
        self._put_status(img, f"MOVE: {f(metrics, 'composite_movement')}", 0)

    def _draw_pullup_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"ELBOW: {f(metrics, 'elbow_angle', True)} | SHOULDER: {f(metrics, 'shoulder_status')}", 1)
        self._put_status(img, f"EXT: {f(metrics, 'extension_status')} | BACK: {f(metrics, 'back_arch_status')}", 0)

    def _draw_lunge_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"KNEE: {f(metrics, 'front_knee_angle', True)} | TORSO: {f(metrics, 'torso_angle', True)}", 1)
        self._put_status(img, f"BALANCE: {f(metrics, 'balance_status')}", 0)

    def _draw_plank_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"BACK: {f(metrics, 'back_angle', True)} | HIP: {f(metrics, 'hip_angle', True)}", 1)
        self._put_status(img, f"BODY: {f(metrics, 'body_alignment')}", 0)

    def _draw_jumping_jack_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"SHOULDER: {f(metrics, 'shoulder_angle', True)} | SWING: {f(metrics, 'swing_status')}", 1)
        self._put_status(img, f"MOVE: {f(metrics, 'composite_movement')}", 0)

    def _draw_mountain_climber_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"KNEE: {f(metrics, 'knee_angle', True)} | HIP: {f(metrics, 'hip_angle', True)}", 2)
        self._put_status(img, f"TORSO: {f(metrics, 'torso_angle', True)}", 1)
        self._put_status(img, f"MOVE: {f(metrics, 'composite_movement')}", 0)

    def _draw_leg_raise_overlays(self, img, metrics):
        f = self._fmt
        self._put_status(img, f"HIP: {f(metrics, 'hip_angle', True)} | TORSO: {f(metrics, 'torso_angle', True)}", 1)
        self._put_status(img, f"EXT: {f(metrics, 'extension_status')}", 0)


    def recv(self,frame):
        image 