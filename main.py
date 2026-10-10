import streamlit as st
import os
import time
import math
from services.state.session_default import initial_session_default
from services.auth.login import render_login_page
from services.config.workout_config import Exercise_options
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass


# Exercises that are measured by TIME (per set) instead of REPS.
# For these, the Reps input is hidden and the countdown timer is used.
TIMED_EXERCISES = {"Jumping Jack", "Planks", "Mountain climbers"}



# COUNTDOWN
# run_every=1 -> Streamlit re-runs ONLY this function every second.
# That way the timer ticks without restarting the whole app (and the camera).
#
# The remaining time is never stored. It is always calculated as:
#       timer_end_at - current_time
# so it can't freeze or drift.
@st.fragment(run_every=1)
def countdown_display():
    remaining = max(0, int(math.ceil(st.session_state["timer_end_at"] - time.time())))
    minutes, seconds = divmod(remaining, 60)
    st.metric("Remaining time", f"{minutes}:{seconds:02d}")

    # Current set finished
    if remaining <= 0:
        st.session_state["sets_completed"] += 1

        if st.session_state["sets_completed"] >= st.session_state["no_of_sets"]:
            # All sets done -> end the workout
            st.session_state["workout_started"] = False
        else:
            # More sets left -> start the next set with the full duration again
            # (set_duration was saved when Start was pressed)
            st.session_state["timer_end_at"] = time.time() + st.session_state["set_duration"]

        # Full app rerun so the sidebar and camera reflect the new state
        st.rerun()


def main():
    st.set_page_config(
        page_icon="bodybuilder",
        page_title="AI Real-time Gym Trainer",
        initial_sidebar_state="expanded",
        layout="centered"
    )

    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static", "Baloo_2", "Baloo2-VariableFont_wght.ttf"), "AdobeClean")

    init_db()  # calling database

    if not render_login_page():
        return

    # Keeps widget values alive between reruns
    for key in ("exercise_name", "no_of_sets", "no_of_reps", "timer_minutes", "timer_seconds"):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]

    initial_session_default()

    workout_started = st.session_state.get("workout_started", False)

    with st.sidebar:
        st.title("Personal Home AI Trainer")

        if st.session_state.username:
            st.caption(f"👤 Logged in as {st.session_state.username}")

        st.divider()

        st.subheader("Workout Plan")

        
        # BEFORE WORKOUT: plan inputs + Start button
        if not workout_started:

            st.selectbox('Exercises', options=Exercise_options, key='exercise_name')

            st.number_input('Sets', min_value=0, max_value=20, key='no_of_sets', step=1)

            # Reps only make sense for rep-based exercises, so hide it for timed ones
                        # Reps only for rep-based exercises, timer only for timed exercises
            is_timed_selected = st.session_state.get("exercise_name") in TIMED_EXERCISES

            if is_timed_selected:
                # Duration of ONE set (timed exercises only)
                minute, seconds = st.columns(2)

                with minute:
                    st.number_input('minutes', min_value=0, max_value=15, key='timer_minutes')

                with seconds:
                    st.number_input('seconds', min_value=0, max_value=60, step=5, key="timer_seconds")
            else:
                st.number_input('Reps', min_value=0, max_value=60, key="no_of_reps", step=1)

            st.markdown("")  # for space

            start_session_button = st.button("Start Workout", width="stretch", key="start_session_button")

            if start_session_button:
                is_timed = st.session_state.exercise_name in TIMED_EXERCISES

                # Only timed exercises have a duration; rep-based ones don't use the timer
                if is_timed:
                    duration = st.session_state.timer_minutes * 60 + st.session_state.timer_seconds
                else:
                    duration = 0

                # Validation
                if is_timed and duration == 0:
                    st.error("Set a timer greater than 0")
                elif st.session_state.no_of_sets == 0:
                    st.error("Set at least 1 set")
                elif not is_timed and st.session_state.no_of_reps == 0:
                    st.error("Set at least 1 rep")
                else:
                    st.session_state["set_duration"] = duration
                    st.session_state["sets_completed"] = 0
                    st.session_state["timer_end_at"] = time.time() + duration
                    st.session_state["workout_started"] = True
                    st.rerun()  # to make it work on one click


        
        # DURING WORKOUT: summary, End button, progress, live metrics

        if workout_started:

            exercise = st.session_state.get("exercise_name")
            sets = st.session_state.get("no_of_sets")
            reps = st.session_state.get("no_of_reps")

            # Plan summary: different text for timed vs rep-based exercises
            if exercise in TIMED_EXERCISES:
                m, s = divmod(st.session_state.get("set_duration", 0), 60)
                st.info(f"**{exercise}** -- **{sets} Sets** X **{m}:{s:02d}**")
            else:
                st.info(f"**{exercise}** -- **{sets} Sets**  X **{reps} Reps**")

            end_session_button = st.button("End Workout", width="stretch", key="end_session_button")

            if end_session_button:
                st.session_state["workout_started"] = False
                st.rerun()

            st.divider()

            Total_no_of_reps = st.session_state.get("reps")
            Current_no_of_reps = st.session_state.get("current_reps")
            reps_per_set = st.session_state.get("no_of_reps")
            set_completed = st.session_state.get("sets_completed") or 0
            target_sets = st.session_state.get("no_of_sets") or 0

            st.subheader("Progress")

            if exercise in TIMED_EXERCISES:
                # Timed exercise: show set number and the live countdown
                current_set = min(set_completed + 1, target_sets)
                st.metric("Current set", f"{current_set}/{target_sets}")
                st.metric("Sets completed", f"{set_completed}/{target_sets}")
                countdown_display()  # ticks every second on its own
            else:
                # Rep-based exercise: show reps and sets
                st.metric("Total Reps", f"{Total_no_of_reps}")
                st.metric("Current no of reps", f"{Current_no_of_reps}/{reps_per_set}")
                st.metric("Sets completed", f"{set_completed}/{target_sets}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)

            if exercise == "Push-up":
                st.subheader("Push-up Metrics")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Hip Status", st.session_state.hip_status)
                

            if exercise == "Burpees":
                st.subheader("Burpee Metrics")
                st.metric("Hip Angle", f"{st.session_state.hip_angle}°")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Composite Movement", st.session_state.composite_movement)

            if exercise == "Pull-ups":
                st.subheader("Pull-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Status", st.session_state.shoulder_status)
                st.metric("Extension Status", st.session_state.extension_status)
                st.metric("Back Arch Status", st.session_state.back_arch_status)

            if exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle", f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)

            # TIME BASED
            if exercise == "Planks":
                st.subheader("Plank Metrics")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Hip Angle", f"{st.session_state.hip_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)

            if exercise == "Jumping Jack":
                st.subheader("Jumping Jack Metrics")
                st.metric("Shoulder Angle", f"{st.session_state.shoulder_angle}°")  # label fixed
                st.metric("Swing Status", st.session_state.swing_status)
                st.metric("Composite Movement", st.session_state.composite_movement)

            if exercise == "Mountain climbers":
                st.subheader("Mountain Climber Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Hip Angle", f"{st.session_state.hip_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Composite Movement", st.session_state.composite_movement)

            if exercise == "Leg-Raises":
                st.subheader("Leg Raise Metrics")
                st.metric("Hip Angle", f"{st.session_state.hip_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Extension Status", st.session_state.extension_status)

   
    # MAIN PAGE

    st.title("Real-Time AI GYM Trainer")
    st.markdown("Real-Time form Detection with Proactive AI voice Trainer")

    if not workout_started:
        st.markdown("""
            <div style="
                border: 10px dashed #444;
                border-radius: 0px;
                padding: 48px 32px;
                text-align: center;
                color: #888;
                margin-top: 32px;
            ">
                <h2 style="color:#ccc; margin-bottom:8px;">👉 Set your workout plan</h2>
                <p style="font-size:1.05rem;">
                    Choose your exercise, sets and reps in the sidebar,<br>
                    then click <strong>Start Workout</strong> to activate the camera and AI Trainer
                </p>
            </div>
            """, unsafe_allow_html=True)

    else:
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        inject_webrtc_styles(os.path.join(os.getcwd(), "static", "Baloo_2", "Baloo2-VariableFont_wght.ttf"), "AdobeClean")

    # for workout history
    st.markdown("### Workout History")
    


if __name__ == "__main__":
    main()