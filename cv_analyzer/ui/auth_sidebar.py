import streamlit as st

from cv_analyzer.auth import AuthService
from cv_analyzer.ui.session import get_current_user, logout, set_current_user


def render_auth_sidebar() -> None:
    user = get_current_user()
    auth = AuthService()

    with st.sidebar:
        st.header("Hesap")

        if user:
            st.write(f"Merhaba, {user['full_name']}")
            st.caption(user["email"])
            if st.button("Çıkış", use_container_width=True):
                logout()
                st.rerun()
            return

        st.caption("Giriş yapmadan da kullanabilirsiniz.")

        mode = st.radio("", ["Giriş", "Kayıt"], horizontal=True, label_visibility="collapsed")

        if mode == "Giriş":
            email = st.text_input("E-posta", key="login_email")
            password = st.text_input("Şifre", type="password", key="login_password")
            if st.button("Giriş yap", use_container_width=True, type="primary"):
                logged_in, message = auth.login(email, password)
                if logged_in:
                    set_current_user(logged_in)
                    st.rerun()
                else:
                    st.error(message)
        else:
            full_name = st.text_input("Ad soyad", key="register_name")
            email = st.text_input("E-posta", key="register_email")
            password = st.text_input("Şifre", type="password", key="register_password")
            password2 = st.text_input("Tekrar", type="password", key="register_password2")
            if st.button("Kayıt ol", use_container_width=True, type="primary"):
                if password != password2:
                    st.error("Şifreler uyuşmuyor.")
                else:
                    ok, message = auth.register(email, password, full_name)
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)
