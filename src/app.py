from pathlib import Path

import dotenv
from quart import Quart

from routes import mount_routes

dotenv.load_dotenv()


def create_app() -> Quart:
    app = Quart(__name__, instance_relative_config=True)

    Path(app.instance_path).mkdir(exist_ok=True)

    app.config.from_pyfile("config.py")

    mount_routes(app)

    return app
