import streamlit as st

from services.auth.login import render_login_page

def main():
    st.set_page_config(
       page_icon="bodybuilder",
       page_title="AI Real-time Gym Trainer",
       initial_sidebar_state="expanded",
       layout="centered"
    )

    if not render_login_page():
       return

if __name__ == "__main__":
    main()