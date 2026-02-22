import asyncio
import json
import time

from quart import request, websocket
from werkzeug.exceptions import UnsupportedMediaType

import settings
from services import MonitorService, SMTPService
from types_ import MonitorResultDetailsResponse, MonitorResultResponse, TestResult


class MonitorController:
    def __init__(self, monitor_service: MonitorService, smtp_service: SMTPService):
        self.monitor_service = monitor_service
        self.smtp_service = smtp_service

    async def http_monitor(self):
        json: dict | None = await request.get_json()

        if not json:
            raise UnsupportedMediaType()

        config = settings.MonitorSettings(**json)
        results = await self.monitor_service.test_all(config)
        processed = self._process_results(results)

        return processed, 200

    async def ws_monitor(self):
        config_data = await websocket.receive_json()

        config = settings.WebSocketSettings(**config_data)

        last_email_sent = 0

        while True:
            try:
                results = await self.monitor_service.test_all(config)

                processed = self._process_results(results)

                if time.time() - last_email_sent > config.notify_error_interval:
                    asyncio.create_task(
                        self._send_email_error_report(
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

    def _process_results(self, results: list[TestResult]) -> MonitorResultResponse:
        success = True
        details: list[MonitorResultDetailsResponse] = []

        for res in results:
            if success and not res.success:
                success = False
            details.append(
                {
                    "url": f"{res.domain}{res.endpoint}",
                    "status_code": res.status_code,
                    "success": res.success,
                    "error": res.error,
                    "latency_ms": round(res.latency_ms, 3),
                }
            )
        return {
            "ok": success,
            "details": details,
        }

    async def _send_email_error_report(
        self,
        config: settings.MonitorSettings,
        subject: str,
        report: MonitorResultResponse,
    ):
        if config.notify_on_error and not report["ok"] and config.email:
            await self.smtp_service.send_email(
                config.email, subject, json.dumps(report, indent=4)
            )
