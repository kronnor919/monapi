import os
from pathlib import Path

import dotenv
from quart import Quart

from controllers import MonitorController
from routes import mount_routes
from services import MonitorService, SMTPService
from settings import SMTPSettings

dotenv.load_dotenv()


def create_app() -> Quart:
    app = Quart(__name__, instance_relative_config=True)

    Path(app.instance_path).mkdir(exist_ok=True)

    app.config.from_pyfile("config.py")

    # Settings
    smtp_settings = SMTPSettings(
        host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=os.getenv("SMTP_EMAIL", ""),
        password=os.getenv("SMTP_PASSWORD", ""),
    )

    # Services
    monitor_service = MonitorService()
    smtp_service = SMTPService(smtp_settings)

    # Controllers
    monitor_controller = MonitorController(monitor_service, smtp_service)

    mount_routes(app, monitor_controller)

    return app
