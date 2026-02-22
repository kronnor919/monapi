from dataclasses import dataclass
from typing import Any, Literal, TypedDict

Headers = dict[str, Any]
Params = dict[str, Any]
Body = dict[str, Any]
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE"]


@dataclass
class TestResult:
    success: bool
    domain: str
    endpoint: str
    status_code: int
    latency_ms: float
    error: str | None = None


class MonitorResultDetailsResponse(TypedDict):
    success: bool
    url: str
    status_code: int
    latency_ms: float
    error: str | None


class MonitorResultResponse(TypedDict):
    ok: bool
    details: list[MonitorResultDetailsResponse]
