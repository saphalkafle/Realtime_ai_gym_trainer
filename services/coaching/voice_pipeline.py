import time
import streamlit as st

class VoicePipeline:
    def __init__(self,llm,tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0  #to improve user experience

        def _find_form_issue(self, exercise, metrics):
            if "issue" in metrics:
                return metrics["issue"]

            def angle(key):
                # 0 means the landmarks were not visible, so ignore it
                v = metrics.get(key)
                return v if isinstance(v, (int, float)) and v > 0 else None

            back = angle("back_angle")
            torso = angle("torso_angle")
            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")
            movement = metrics.get("composite_movement", "")

            # each check: (name, is_it_happening_now, message, seconds it must last)
            checks = []

            if exercise == "Squats":
                checks = [
                    ("squat_lean", back is not None and back < 45,
                    "The user is folding too far forward during the squat — keep the chest up.", 1.0),
                ]
            elif exercise == "Push-up":
                checks = [
                    ("pushup_sag", hip_status == "Sagging",
                    "The user's hips are sagging down during the push-up.", 1.0),
                    ("pushup_pike", hip_status == "Picked up",
                    "The user's hips are too high — lower them to form a straight line.", 1.0),
                    ("pushup_body", alignment == "Poor Form",
                    "The user's body is not straight during the push-up.", 1.0),
                ]
            elif exercise == "Burpees":
                checks = [
                    ("burpee_body", alignment == "Poor",
                    "The user's body is not in a straight line in the plank / push-up part of the burpee.", 1.0),
                ]
            elif exercise == "Pull-ups":
                arch = metrics.get("back_arch_status", "")
                checks = [
                    ("pullup_arch_big", arch == "Excessive Arch",
                    "The user is arching their back excessively during the pull-up.", 1.0),
                    ("pullup_arch_small", arch == "Slight Arch",
                    "Slight back arch detected — encourage the user to brace their core.", 2.0),
                ]
            elif exercise == "Lunges":
                checks = [
                    ("lunge_balance", metrics.get("balance_status", "") == "OFF BALANCE",
                    "The user is losing balance during the lunge — keep the upper body over the hips.", 1.0),
                ]
            elif exercise == "Planks":
                checks = [
                    ("plank_sag", "Hips Sagging" in alignment,
                    "The user's hips are sagging during the plank — lift them into a straight line.", 1.0),
                    ("plank_raised", "Hips Raised" in alignment,
                    "The user's hips are too high during the plank — lower them into a straight line.", 1.0),
                    ("plank_poor", alignment == "Poor Form",
                    "The user's body is not straight during the plank.", 1.0),
                ]
            elif exercise == "Jumping Jack":
                checks = [
                    ("jj_incomplete", movement == "INCOMPLETE",
                    "The user is not completing the jumping jack — arms fully up with legs wide, then fully down.", 2.0),
                ] 
            elif exercise == "Mountain climbers":
                checks = [
                    ("mc_posture", movement == "BAD POSTURE",
                    "The user's hips or shoulders are too high during mountain climbers — keep the body flat like a plank.", 1.0),
                ]
            elif exercise == "Leg-Raises":
                checks = [
                    ("legraise_bent", metrics.get("extension_status", "") == "BENT",
                    "The user's knees are bending during the leg raise — keep the legs straight.", 1.0),
                    ("legraise_torso", torso is not None and torso > 25,
                    "The user's upper body is lifting off the floor during the leg raise.", 1.0),
                ]

            # A problem only counts after it has lasted `seconds` without stopping,
            # so one bad frame never triggers feedback.
            if not hasattr(self, "_issue_since"):
                self._issue_since = {}

            now = time.time()
            found = None
            for name, happening, message, seconds in checks:
                if happening:
                    started = self._issue_since.setdefault(name, now)
                    if found is None and now - started >= seconds:
                        found = message
                else:
                    self._issue_since.pop(name, None)

            return found

    def process_event(self,event,exercise,metrics):
        issue = self._find_form_issue(exercise,metrics)


        now = time.time()

        is_major_issue = event in ["workout_started","set_completed","workout_completed"]

        if not is_major_issue:
            if not issue:
                return None

            if now - self.last_spoken_at <5:
                return None


        text = self.llm.give_feedback(event,issue)
        voice = self.tts.speak(text)

        self.last_spoken_at = now
        return voice, text

    def autoplay_audio(audio_bytes):
        if not audio_bytes:
            return

        st.markdown("<style>[data-testid='stAudio'] {display:none;}</style>",unsafe_allow_html=True)
        st.audio(audio_bytes,format="audio/mp3",autoplay=True)

