from __future__ import annotations

from dataclasses import dataclass
from shutil import rmtree
from typing import TYPE_CHECKING, Union

from flask_login import (  # type: ignore
    UserMixin, current_user, login_user, logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from pandas import DataFrame, read_sql
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.security import check_password_hash, generate_password_hash

from .settings import DATA_DIR, USERS_FILE


class Users(SQLAlchemy):
    __file__ = DATA_DIR / "users.sqlite"

    def init(self, app) -> None:
        self.init_app(app)
        with app.app_context():
            self.create_all()
            if self.empty:
                self.append({"username": "default", "password": "default", "admin": True})
                if USERS_FILE.exists():
                    with open(USERS_FILE) as users:
                        for user in users:
                            self.append({"username": user.strip(), "password": "default", "admin": False})

    def append(self, form: dict) -> None:
        try:
            user = self[form["username"]]
        except UserException:
            user = None

        if not user:
            user = User(username=form["username"], password=generate_password_hash(form["password"]), admin=bool(form.get("admin")))
            self.session.add(user)
            self.session.commit()
        else:
            raise UserException("User already exists!")

    def __getitem__(self, idx: Union[int, str]) -> User:
        if isinstance(idx, int):
            username = self._table.at[idx, "username"]
        elif isinstance(idx, str):
            username = idx
        user = User.query.filter_by(username=username).first()

        if not user:
            raise UserException("Invalid user!")
        return user

    def __delitem__(self, idx: int) -> None:
        user = self[idx]
        self.session.delete(user)
        self.session.commit()

        user_data = DATA_DIR / user.username
        if user_data.exists():
            rmtree(user_data)

    def __len__(self) -> int:
        return User.query.count()

    @property
    def empty(self) -> bool:
        return not len(self)

    @property
    def _table(self) -> DataFrame:
        return read_sql(User.query.statement, self.engine)

    @property
    def _columns(self) -> list:
        return self._table.columns.tolist()

    @property
    def _values(self) -> list:
        return self._table.values.tolist()

    @property
    def table(self) -> DataFrame:
        return self._table.drop(["id", "password"], axis=1)

    @property
    def columns(self) -> list:
        return self.table.columns.tolist()

    @property
    def values(self) -> list:
        return self.table.values.tolist()

    # ------------------------------ User Management ----------------------------- #

    def login(self, form: ImmutableMultiDict) -> None:
        user = self[form["username"]]
        if not user:
            raise UserException("Invalid user!")

        if not check_password_hash(user.password, form["password"]):
            raise UserException("Invalid password!")

        login_user(user)

    def logout(self) -> None:
        logout_user()

    def change_password(self, form: ImmutableMultiDict) -> None:
        user = self[current_user.username]
        if not user:
            raise UserException("Invalid user!")

        if form["password_new"] is not form["password_check"]:
            raise UserException("Passwords do not match!")
        if not check_password_hash(user.password, form["password_old"]):
            raise UserException("Invalid password!")

        user.password = generate_password_hash(form["password_new"])
        self.session.commit()

    def reset_password(self, idx: int, form: ImmutableMultiDict) -> None:
        user = self[idx]
        if not user:
            raise UserException("Invalid user!")

        if form["password_new"] is not form["password_check"]:
            raise UserException("Passwords do not match!")

        user.password = generate_password_hash(form["password_new"])
        self.session.commit()

users = Users()

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = users.Model

@dataclass
class User(Model, UserMixin):
    id: int = users.Column(users.Integer, primary_key=True)
    username: str = users.Column(users.String(100), nullable=False, unique=True)
    password: str = users.Column(users.String(100), nullable=False)
    admin: bool = users.Column(users.Boolean, nullable=False, default=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.username == other.username

class UserException(Exception):
    def __init__(self, message: str = "Unknown error!") -> None:
        self.message = message
        super().__init__(message)
