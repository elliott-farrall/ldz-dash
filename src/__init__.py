import logging
from json import load

from dotenv import dotenv_values
from flask import Flask

from .blueprints import root
from .data import Data
from .login import login
from .settings import DATA_DIR, OPTIONS_DIR, STATIC_DIR
from .user import users


class App(Flask):
    def __init__(self) -> None:
        super().__init__(__name__)

        # ---------------------------------- Config ---------------------------------- #

        self.config.from_mapping(dotenv_values())
        self.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{users.__file__}"

        DATA_DIR.mkdir(exist_ok=True)

        # -------------------------------- Initialise -------------------------------- #

        login.init(self)
        users.init(self)

        self.register_blueprint(root)

        # -------------------------------- Environment ------------------------------- #

        @self.context_processor
        def global_vars() -> dict:
            with (
                open(OPTIONS_DIR / "departments.json") as departments_file,
                open(OPTIONS_DIR / "levels.json") as levels_file,
                open(OPTIONS_DIR / "locations.json") as locations,
                open(OPTIONS_DIR / "referrals.json") as referrals,
                open(OPTIONS_DIR / "topics.json") as topics_file,
            ):
                return {
                    "styles": [file.name for file in STATIC_DIR.iterdir()],
                    "categories": Data.categories,
                    "departments": load(departments_file),
                    "levels": load(levels_file),
                    "locations": load(locations),
                    "referrals": load(referrals),
                    "topics": load(topics_file),
                }

app = App()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="flask.log")
    app.run()
