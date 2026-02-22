import asyncio
import json
import time

from quart import Quart, request, websocket
from werkzeug.exceptions import UnsupportedMediaType

import settings
from monitor import test_all
from smtp import send_email
from types_ import MonitorResultDetailsResponse, MonitorResultResponse, TestResult


async def send_email_error_report(
    config: settings.MonitorSettings, subject: str, report: MonitorResultResponse
):
    if config.notify_on_error and not report["ok"] and config.email:
        await send_email(config.email, subject, json.dumps(report, indent=4))


def process_results(results: list[TestResult]) -> MonitorResultResponse:
    success = True
    details: list[MonitorResultDetailsResponse] = []

    for res in results:
        if success and not res.success:
            success = False
        details.append({
            "url": f"{res.domain}{res.endpoint}",
            "status_code": res.status_code,
            "success": res.success,
            "error": res.error,
            "latency_ms": round(res.latency_ms, 3),
        })
    return {
        "ok": success,
        "details": details,
    }


def mount_routes(app: Quart):
    @app.post("/monitor")
    async def monitor():
        json: dict | None = await request.get_json()

        if not json:
            raise UnsupportedMediaType()

        config = settings.MonitorSettings(**json)
        results = await test_all(config)
        processed = process_results(results)

        return processed, 200

    @app.websocket("/ws/monitor")
    async def _ws_monitor():
        config_data = await websocket.receive_json()

        config = settings.WebSocketSettings(**config_data)

        last_email_sent = 0

        while True:
            try:
                results = await test_all(config)

                processed = process_results(results)

                if time.time() - last_email_sent > config.notify_error_interval:
                    asyncio.create_task(
                        send_email_error_report(
                            config,
                            "API Monitor Error",
                            processed,
                        )
                    )
                    last_email_sent = time.time()

                await websocket.send_json(processed)

                await asyncio.sleep(config.monitoring_interval)

            except asyncio.CancelledError:
                break
