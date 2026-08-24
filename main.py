import streamlit as st
from services.state.session_default import initial_session_default
from services.auth.login import render_login_page
from services.config.workout_names import Exercise_options

def main():
    st.set_page_config(
       page_icon="bodybuilder",
       page_title="AI Real-time Gym Trainer",
       initial_sidebar_state="expanded",
       layout="centered"
    )

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

         st.number_input('Reps',min_value=0,max_value=100,key='no_of_reps',step=1)

         st.markdown("") #for space

         start_session_button= st.button("Start Workout",width="stretch",key="start_session_button")


         if start_session_button:
            st.session_state["workout_started"] = True
            st.rerun() #to make it work on one click

        else:
            exercise = st.session_state.get("exercise_name")
            sets = st.session_state.get("no_of_sets")
            reps = st.session_state.get("no_of_reps")

            st.info(f"**{exercise}** -- **{sets} Sets**  X **{reps} Reps**")

            end_session_button = st.button("End session" , width = "stretch",key="end_session_button")

            if end_session_button:
               st.session_state["workout_started"] = False
               st.rerun()


        # When workout starts these happens

        if workout_started:

           st.divider()

           exercise = st.session_state.get("exercise_names")
           Total_no_of_reps = st.session_state.get("reps")
           Current_no_of_reps = st.session_state.get("current_reps")
           reps_per_set = st.session_state.get("no_of_reps")
           set_completed = st.session_state.get("sets_completed")
           target_sets = st.session_state.get("no_of_sets")



           st.subheader(f"**Progress**")
           st.metric("Total Reps",f"{Total_no_of_reps}")

           st.metric("Current no of reps",f"{Current_no_of_reps}/{reps_per_set}")
           st.metric("Sets completed",f"{set_completed}/{target_sets}")

           st.divider()

           


        

        

    
if __name__ == "__main__":
    main()