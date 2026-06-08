import re

import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from cv_analyzer.db import User, get_session

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthService:

    def register(self, email: str, password: str, full_name: str) -> tuple[bool, str]:
        email = email.strip().lower()
        full_name = full_name.strip()

        if not full_name:
            return False, "Ad soyad gerekli."
        if not EMAIL_PATTERN.match(email):
            return False, "Geçerli e-posta girin."
        if len(password) < 6:
            return False, "Şifre en az 6 karakter olmalı."

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        try:
            with get_session() as session:
                user = User(email=email, password_hash=password_hash, full_name=full_name)
                session.add(user)
                session.flush()
        except IntegrityError:
            return False, "Bu e-posta zaten kayıtlı."

        return True, "Kayıt tamam, giriş yapabilirsiniz."

    def login(self, email: str, password: str) -> tuple[dict | None, str]:
        email = email.strip().lower()

        with get_session() as session:
            user = session.scalar(select(User).where(User.email == email))
            if user is None:
                return None, "E-posta veya şifre hatalı."

            if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
                return None, "E-posta veya şifre hatalı."

            return {"id": user.id, "email": user.email, "full_name": user.full_name}, "Tamam"
