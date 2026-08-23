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

        if not workout_started:
         
         st.selectbox('Exercises',options=Exercise_options,key='exercise_name')
        
        

    
if __name__ == "__main__":
    main()