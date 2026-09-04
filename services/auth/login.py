import streamlit as st
from services.persistence.exercise_repository import get_or_create_user

def render_login_page():
    if st.session_state.get("user_id") is not None:
        return True

    st.title("AI Real-time Gym Trainer")
    st.markdown("### Please log in to access the application.")

    with st.form("login_form",clear_on_submit=False):
        username = st.text_input("Your Username",placeholder="Enter your username here")
        submit_button = st.form_submit_button("Enter the session")
        

    if submit_button:
        if not username:
            st.error("Name cannot be empty...")
            return False

        user = get_or_create_user(username)

        st.session_state["user_id"]= user["id"]
        st.session_state["username"] = user["username"]
        
        st.rerun()
    return False