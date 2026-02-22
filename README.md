# API Monitor

A real-time API monitoring service with HTTP and WebSocket support. Sends email notifications when endpoints fail.

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

1. Install uv (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create `.env` file in project root:

   ```bash
   touch .env
   ```

3. Add SMTP credentials to `.env`:

   ```text
   SMTP_EMAIL="yourgooglemail@gmail.com"
   SMTP_PASSWORD="your_app_password"
   SMTP_HOST="smtp.gmail.com" # This value is the default
   ```

   > **Note for Gmail users:** You need to use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

4. Configure server (optional) in `src/instance/config.py`:

   ```python
   DEBUG = True
   SERVER_NAME = "localhost:5040"  # Change host:port as needed
   ```

5. Install dependencies:

   ```bash
   uv sync
   ```

6. Run the server:

   ```bash
   python src/run.py
   ```

## Configuration Example

```js
const config = {
    "notify_error_interval": 300,
    "notify_on_error": true,
    "email": "youremail@example.com",
    "domains": [
        {
            "url": "https://api.chucknorris.io",
            "endpoints": [
                {
                    "rule": "/jokes/random",
                    "method": "GET",
                    "expected_status": 200,
                    "body": {},
                    "headers": {},
                    "params": {},
                    "timeout": 10
                }
            ]
        }
    ]
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `notify_error_interval` | float | Seconds between error notification emails (default: 900) |
| `notify_on_error` | bool | Enable email notifications on errors (default: true) |
| `email` | string | Email address to receive notifications |
| `domains` | array | List of domains to monitor |
| `monitoring_interval` | float | Seconds between checks (WebSocket only) |

#### Domain Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Base URL of the API to monitor |
| `endpoints` | array | List of endpoints to test |

#### Endpoint Fields

| Field | Type | Description |
|-------|------|-------------|
| `rule` | string | Endpoint path (e.g., `/health`) |
| `method` | string | HTTP method (`GET`, `POST`, `PUT`, `DELETE`, etc.) |
| `expected_status` | int | Expected HTTP status code |
| `body` | object | Request body (for POST/PUT) |
| `headers` | object | Custom request headers |
| `params` | object | URL query parameters |
| `timeout` | float | Request timeout in seconds |

## Usage

### HTTP Endpoint

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"domains":[{"url":"https://api.example.com","endpoints":[{"rule":"/health","method":"GET","expected_status":200,"body":{},"headers":{},"params":{},"timeout":10}]}]}' \
  http://localhost:5040/monitor
```

### WebSocket

```js
const ws = new WebSocket("ws://localhost:5040/ws/monitor");

ws.onopen = () => {
    ws.send(JSON.stringify({
        ...config,
        "monitoring_interval": 20.0
    }));
};

ws.onmessage = (e) => {
    console.log(JSON.parse(e.data));
};

ws.onerror = (e) => {
    console.error(e);
};
```

## Response Format

```json
{
    "ok": false,
    "details": [
        {
            "url": "https://api.chucknorris.io/jokes/random",
            "status_code": 200,
            "success": true,
            "error": null,
            "latency_ms": 123.456
        }
    ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | bool | `true` if all endpoints passed |
| `details` | array | List of results for each endpoint |
| `details[].url` | string | Full URL that was tested |
| `details[].status_code` | int | HTTP status code returned |
| `details[].success` | bool | Whether status matched expected |
| `details[].error` | string | Error message if failed, `null` otherwise |
| `details[].latency_ms` | float | Response time in milliseconds |
