from quart import Quart

from controllers import MonitorController


def mount_routes(app: Quart, monitor_controller: MonitorController):
    app.get("/health")(
        lambda: ({"success": True, "message": "API Monitor is up and running"}, 200)
    )
    app.post("/monitor")(monitor_controller.http_monitor)
    app.websocket("/ws/monitor")(monitor_controller.ws_monitor)
