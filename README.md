# Google Calendar MCP Server

Quick start
-----------

1. Make the launcher executable and run it:

```bash
chmod +x run.sh
./run.sh
```

2. (Optional) Run using the venv python directly for debugging:

```bash
export GOOGLE_SERVICE_ACCOUNT_KEY=$(cat service-account-key.json)
.venv/bin/python main.py
```

An MCP (Model Context Protocol) server that connects to the Google Calendar API and answers natural language questions about appointments and events.

## Features

- **Natural Language Queries**: Ask questions like "What's on my schedule today?" or "Do I have any meetings tomorrow?"
- **Flexible Time Ranges**: Query events for specific dates, date ranges, or upcoming periods
- **Availability Checking**: Check if specific time slots are free or conflicted
- **Timezone Support**: Handle different timezones for accurate scheduling
- **Structured Responses**: Get formatted, easy-to-read calendar information

## Setup

### 1. Google Calendar API Setup (Service Account)

This project uses a service account by default (no OAuth redirect flow needed).

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "Service Account"
6. Create the service account and download the JSON key file
7. **Important**: Share your Google Calendar with the service account email address (found in the JSON file as `client_email`)

### 2. Configuration

**For Service Account:**
1. Copy the service account JSON file to `service-account-key.json`, OR
2. Set as environment variable:
   ```bash
   export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
   ```

### 3. Installation

Install required dependencies:
```bash
pip install google-auth google-auth-oauthlib google-api-python-client mcp python-dateutil pytz
```

## Tests / Local checks

There are simple test scripts in the repo to validate authentication and MCP handlers:

- `test_auth.py` — verifies the Google Calendar authentication and attempts to fetch a few events.
- `test_mcp_driver.py` — exercises the MCP handlers directly (no MCP transport layer).
- `test_mcp_queries.py` — runs a few example natural-language queries against the handlers.

Run them with the venv python and the service account env var set:

```bash
export GOOGLE_SERVICE_ACCOUNT_KEY=$(cat service-account-key.json)
.venv/bin/python test_auth.py
.venv/bin/python test_mcp_driver.py
.venv/bin/python test_mcp_queries.py
```

## Notes and repo changes

- `run.sh` is the canonical launcher for this repo (it replaces older `run_calendar.sh` behavior).
- `main_network.py` was removed — it was empty and unused.
