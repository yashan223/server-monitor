# CoD4 Server Monitor

A simple Python script that monitors a CoD4 `serverstatus.xml` file and sends Telegram alerts when the server goes offline or comes back online.

## Features

- Monitor `serverstatus.xml`
- Detect frozen timestamps
- Detect missing XML file
- Send Telegram notifications
- Lightweight and easy to use

## Setup

1. Install Python 3.
2. Edit the script and set:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
XML_PATH = "/path/to/serverstatus.xml"
```

3. Run the script:

```bash
python3 monitor.py
```
