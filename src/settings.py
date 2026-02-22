from pydantic import BaseModel, EmailStr, ValidationError, field_validator

from types_ import Body, Headers, HTTPMethod, Params


class EndpointSettings(BaseModel):
    rule: str
    method: HTTPMethod
    headers: Headers
    body: Body
    params: Params
    expected_status: int
    timeout: float | None


class DomainSettings(BaseModel):
    url: str
    endpoints: list[EndpointSettings]


class MonitorSettings(BaseModel):
    domains: list[DomainSettings]
    email: EmailStr | None
    notify_on_error: bool = True
    notify_error_interval: float = 60 * 15

    @field_validator("notify_error_interval")
    def notify_error_interval_validator(cls, value: float):
        if value <= 0:
            raise ValidationError("notify_error_interval must be greater than 0")


class WebSocketSettings(MonitorSettings):
    monitoring_interval: float

    @field_validator("monitoring_interval")
    def monitoring_interval_validator(cls, value: float):
        if value <= 0:
            raise ValidationError("monitoring_interval must be greater than 0")
