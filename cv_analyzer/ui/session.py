import streamlit as st


def init_session_state() -> None:
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"


def get_current_user() -> dict | None:
    return st.session_state.get("user")


def set_current_user(user: dict | None) -> None:
    st.session_state.user = user


def logout() -> None:
    st.session_state.user = None
