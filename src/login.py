from typing import Optional

from flask import Flask
from flask_login import LoginManager  # type: ignore

from .user import User


class Login(LoginManager):
    login_view = "root.auth.login"

    def init(self, app: Flask) -> None:
        self.init_app(app)

        @self.user_loader
        def load_user(user_id: str) -> Optional[User]:
            return User.query.get(int(user_id))

login = Login()
