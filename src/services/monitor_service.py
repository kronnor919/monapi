import asyncio
import time

import httpx

from settings import EndpointSettings, MonitorSettings
from types_ import TestResult


class MonitorService:
    async def test_endpoint(
        self, client: httpx.AsyncClient, domain: str, endpoint_setting: EndpointSettings
    ) -> TestResult:
        try:
            start = time.perf_counter()
            response = await client.request(
                method=endpoint_setting.method,
                url=f"{domain}{endpoint_setting.rule}",
                headers=endpoint_setting.headers,
                params=endpoint_setting.params,
                data=endpoint_setting.body,
                timeout=endpoint_setting.timeout or 10,
            )
            latency_ms = (time.perf_counter() - start) * 1000

        except httpx.TimeoutException:
            return TestResult(
                success=False,
                domain=domain,
                endpoint=endpoint_setting.rule,
                status_code=504,
                error="Timeout",
                latency_ms=0,
            )

        except httpx.HTTPError as e:
            return TestResult(
                success=False,
                domain=domain,
                endpoint=endpoint_setting.rule,
                status_code=500,
                error=str(e),
                latency_ms=0,
            )

        return TestResult(
            success=response.status_code == endpoint_setting.expected_status,
            domain=domain,
            endpoint=endpoint_setting.rule,
            status_code=response.status_code,
            error=response.text
            if response.status_code != endpoint_setting.expected_status
            else None,
            latency_ms=latency_ms,
        )

    async def test_all(self, test_config: MonitorSettings) -> list[TestResult]:
        async with httpx.AsyncClient() as client:
            tasks = [
                self.test_endpoint(client, domain.url, endpoint)
                for domain in test_config.domains
                for endpoint in domain.endpoints
            ]
            return await asyncio.gather(*tasks)
