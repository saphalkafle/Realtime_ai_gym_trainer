import streamlit as st

def initial_session_default():
    defaults ={
        "reps":0,
        "target_sets":0,
        "reps_per_set":0,
        "sets_completed":0,
        "current_reps":0,
        "workout_complete":False,
        "last_notified_sets_completed":0,
        "last_notified_workout_complete":False,
        "last_saved_sets_completed":0,
        "set_time_started_at":0.0,
        "last_exercise_type":"squats",

        #workout plan (set before starting)
        "workout_started":False,
        "exercise_name":"Squats",
        "no_of_sets":3,
        "no_of_reps":10,

        #common Angles
        "knee_angle":0,
        "hip_angle":0,
        "heel_angle":0,
        "back_angle":0,
        "elbow_angle":0,
        "torso_angle":0,
        "front_knee_angle":0,

        #status fields
        "depth_status":"N/A",
        "body_alignment":"N/A",
        "hip_status":"N/A",
        "shoulder_status":"N/A",
        "swing_status":"N/A",
        "extension_status":"N/A",
        "back_arch_status":"N/A",
        "balance_status":"N/A",
        "composite_movement":"N/A"
    }

    for key,value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
