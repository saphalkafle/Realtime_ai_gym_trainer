import streamlit as st
import os
from services.state.session_default import initial_session_default
from services.auth.login import render_login_page
from services.config.workout_names import Exercise_options
import time
from services.ui.style_loader import load_css , inject_local_font
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer,WebRtcMode


def main():
    st.set_page_config(
       page_icon="bodybuilder",
       page_title="AI Real-time Gym Trainer",
       initial_sidebar_state="expanded",
       layout="centered"
    )

    load_css(os.path.join(os.getcwd(),"static","style.css"))
    inject_local_font(os.path.join(os.getcwd(),"static","Baloo_2","Baloo2-VariableFont_wght.ttf"),"AdobeClean")

    init_db() #calling database


    if not render_login_page():
       return

    initial_session_default()

    workout_started = st.session_state.get("workout_started",False)

    with st.sidebar:
        st.title("Personal Home AI Trainer")

        if st.session_state.username:
            st.caption(f"👤 Logged in as {st.session_state.username}")

        st.divider()

        st.subheader("Workout Plan")


        # When workout is not started these things are shown
        if not workout_started:
         
         st.selectbox('Exercises',options=Exercise_options,key='exercise_name')

         st.number_input('Sets',min_value=0,max_value=20,key='no_of_sets',step=1)

         st.number_input('Reps',min_value=0,max_value=60,key="no_of_reps",step=1)

         #for timer based exercise
         minute,seconds= st.columns(2)

         with minute :
            st.number_input('minutes',min_value=0,max_value=15,key='timer_minutes')

         with seconds:
            st.number_input('seconds',min_value=0,max_value=60,step=5,key="timer_seconds")

         

         st.markdown("") #for space

         start_session_button= st.button("Start Workout",width="stretch",key="start_session_button")


         if start_session_button:
            
            duration = (st.session_state.timer_minutes*60 + st.session_state.timer_seconds)
            st.session_state["timer_end_at"] = time.time() + duration
            st.session_state["workout_started"] = True
            st.rerun() #to make it work on one click

        else:
            exercise = st.session_state.get("exercise_name")
            sets = st.session_state.get("no_of_sets")
            reps = st.session_state.get("no_of_reps")
            
             
            st.info(f"**{exercise}** -- **{sets} Sets**  X **{reps} Reps**")

            end_session_button = st.button("End Workout" , width = "stretch",key="end_session_button")

            if end_session_button:
               st.session_state["workout_started"] = False
               st.rerun()


        # When workout starts these happens

        if workout_started:

           st.divider()

           exercise = st.session_state.get("exercise_name")
           Total_no_of_reps = st.session_state.get("reps")
           Current_no_of_reps = st.session_state.get("current_reps")
           reps_per_set = st.session_state.get("no_of_reps")
           set_completed = st.session_state.get("sets_completed")
           target_sets = st.session_state.get("no_of_sets")

           #for timer_display
           timer_display = f"{st.session_state.timer_minutes}:{st.session_state.timer_seconds:02d}"



           st.subheader(f"**Progress**")
           st.metric("Total Reps",f"{Total_no_of_reps}")

           st.metric("Current no of reps",f"{Current_no_of_reps}/{reps_per_set}")
           st.metric("Sets completed",f"{set_completed}/{target_sets}")
           st.metric("Remaining time",timer_display)

           #for countdown
           

          

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
               st.metric("Shoulder Status", st.session_state.shoulder_status)

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
               st.metric("Back Knee Angle", f"{st.session_state.knee_angle}°")
               st.metric("Hip Angle", f"{st.session_state.hip_angle}°")
               st.metric("Balance Status", st.session_state.balance_status)

            # TIME BASED
           if exercise == "Planks":
               st.subheader("Plank Metrics")
               st.metric("Back Angle", f"{st.session_state.back_angle}°")
               st.metric("Hip Angle", f"{st.session_state.hip_angle}°")
               st.metric("Body Alignment", st.session_state.body_alignment)

           if exercise == "Jumping Jack":
               st.subheader("Jumping Jack Metrics")
               st.metric("Wrist Angle", f"{st.session_state.wrist_angle}°")
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
            key = "exercise-analysis",
            mode = WebRtcMode.SENDRECV,
            video_processor_factory = None,
            rtc_configuration = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints = {
                "video":True,
                "audio":False
            },
            async_processing=True
        )



    









        
if __name__ == "__main__":
    main()