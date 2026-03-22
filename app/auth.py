import base64
import hashlib
import hmac
import os
import secrets
import pickle
from dataclasses import dataclass
from typing import Optional

from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from . import models
from .database import SessionLocal


serializer = URLSafeSerializer(
    secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
    salt="auth-cookie",
)
COOKIE_NAME = "session"
PBKDF2_ITERATIONS = 600_000


@dataclass
class UserCookie:
    name: str
    session: str


class UserGalaxyNumber:
    def __init__(self, name: str, number_cups: int = 0, number_fingers: int = 10, number_age: int = 7):
        self.name = name
        self.number_cups = number_cups # Количество кружек кофе в неделю
        self.number_fingers = number_fingers # Количество пальцев на руках
        self.number_age = number_age # Возраст человека, если бы он родился 7 лет назад

        self.galaxy_number = self.calc_galaxy_number()
        self.add_to_base()


    def calc_galaxy_number(self):
        return self.number_cups * 123 - self.number_fingers * 3 + self.number_age * 100

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["galaxy_number"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.galaxy_number = self.calc_galaxy_number()
        self.add_to_base()

    def add_to_base(self):
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == self.name).first()
            if not user:
                raise ValueError(f"User '{self.name}' not found")

            galaxy_number = models.GalaxyNumber(
                user_id=user.id,
                number=self.galaxy_number,
            )

            db.add(galaxy_number)
            db.commit()
        finally:
            db.close()


def hash_password(password: str) -> str:
    salt_hex = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ITERATIONS,
    )
    digest_b64 = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_hex}${digest_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, expected_b64 = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        actual_b64 = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
        return hmac.compare_digest(actual_b64, expected_b64)
    except (ValueError, TypeError):
        return False


def create_session(db: Session, user: models.User) -> str:
    token = secrets.token_urlsafe(32)
    db_session = models.UserSession(token=token, user_id=user.id)
    db.add(db_session)
    db.commit()
    bytes_user = pickle.dumps(UserCookie(name=user.username, session=token))
    base64_user = base64.b64encode(bytes_user).decode("utf-8")
    return base64_user


def read_cookie_value(cookie_value: str) -> Optional[UserCookie]:
    try:
        bytes_user = base64.b64decode(cookie_value.encode("utf-8"))
        user = pickle.loads(bytes_user)
        return user
    except (BadSignature, KeyError, TypeError):
        return None


def get_current_user_from_cookie(db: Session, cookie_value: Optional[str]) -> Optional[models.User]:
    if not cookie_value:
        return None

    parsed_cookie = read_cookie_value(cookie_value)
    if not parsed_cookie:
        return None

    session_row = (
        db.query(models.UserSession)
        .join(models.User)
        .filter(
            models.UserSession.token == parsed_cookie.session,
            models.User.username == parsed_cookie.name,
        )
        .first()
    )
    return session_row.user if session_row else None
