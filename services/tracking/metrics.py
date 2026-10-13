import streamlit as st
from services.config.workout_config import METRICS_FIELDS


def sync_metrics_update(context):
    if not context or not hasattr(context,"state") or not context.state.playing:
        return


    processor = getattr(context, "video_processor",None)


    if not processor:
        return 

    exercise = st.session_state.get("exercise_name")

    if not exercise:
        return


    processor.set_exercise(exercise)
    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        return

    reps = latest_metrics.get("reps")
    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)

    if not fields:
        return

    for key,default in fields.items():
        st.session_state[key] = latest_metrics.get(key,default)

    reps_per_set = st.session_state.get("no_of_reps",0)
    target_sets = st.session_state.get("no_of_sets",0)

    if reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        Current_no_of_reps = reps % reps_per_set
        workout_completed = sets_completed >= target_sets

    else:
        sets_completed = 0
        Current_no_of_reps = 0
        workout_completed = False


    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = Current_no_of_reps
    st.session_state.workout_completed = workout_completed




