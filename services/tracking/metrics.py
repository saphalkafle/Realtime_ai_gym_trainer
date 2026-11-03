import streamlit as st
import time
from services.config.workout_config import METRICS_FIELDS, TIMED_EXERCISES
from services.persistence.exercise_repository import add_exercise
import main


def sync_metrics_update(context):
    if not context or not hasattr(context, "state") or not context.state.playing:
        return

    processor = getattr(context, "video_processor", None)
    if not processor:
        return

    exercise = st.session_state.get("exercise_name")
    if not exercise:
        return

    # ALWAYS tell the camera thread which exercise to analyse
    processor.set_exercise(exercise)

    latest_metrics = processor.get_latest_metrics()
    if not latest_metrics:
        return

    # ignore data produced by a different exercise (e.g. first frames)
    if latest_metrics.get("exercise") != exercise:
        return

    fields = METRICS_FIELDS.get(exercise)
    if not fields:
        return

    # copy angles / statuses to session_state for the sidebar
    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    # Timed exercises have no reps. The timer in main.py handles their sets.
    if exercise in TIMED_EXERCISES:
        return

    reps = latest_metrics.get("reps") or 0
    st.session_state.reps = reps

    reps_per_set = st.session_state.get("no_of_reps", 0)
    target_sets = st.session_state.get("no_of_sets", 0)

    if reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        current_reps = reps % reps_per_set
        workout_complete = sets_completed >= target_sets
    else:
        sets_completed = 0
        current_reps = 0
        workout_complete = False

    st.session_state.sets_completed = sets_completed
    st.session_state.current_reps = current_reps          
    st.session_state.workout_complete = workout_complete  

    last_saved_sets = st.session_state.get("last_saved_sets_completed", 0)

    if target_sets > 0 and reps_per_set > 0 and sets_completed > last_saved_sets:
        newly_completed = sets_completed - last_saved_sets
        now_ts = time.time()
        started_at = st.session_state.get("set_time_started_at", now_ts)
        time_taken = int(now_ts - started_at)
        user_id = st.session_state.get("user_id", 0)

        add_exercise(user_id, exercise, newly_completed * reps_per_set, newly_completed, time_taken)

        if st.session_state.get("voice_pipeline"):
            result = st.session_state.voice_pipeline.process_event(
                event = "set_completed",
                exercise = exercise,
                metrics = latest_metrics,
            )

        st.session_state.set_time_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed


    if workout_completed and not st.session_state.get("last_notified_workout_complete",False):
        st.session_state.last_notified_workout_complete = True

        if st.session_state.get("voice_pipeline"):
            result = st.session_state.voice_pipeline.process_event(
                event="workout_completed",
                exercise=exercise,
                metrics=latest_metrics
            )

            if result:
                st.session_state.audio_to_play,st.session_state.coach_feedback = result

    
    if workout_complete:
        st.session_state.workout_started = False
        st.rerun()