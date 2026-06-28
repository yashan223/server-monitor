import xml.etree.ElementTree as ET
import time
import urllib.request
import urllib.parse
import json
import sys
from datetime import datetime

BOT_TOKEN = ""
CHAT_ID   = ""
XML_PATH  = r"/home/cod4/serverstatus.xml"
STALE_THRESHOLD = 40
CHECK_INTERVAL  = 15
SERVER_NAME = "Ceylon Warfare SND"


def log(msg: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}]  {msg}", flush=True)


def send_telegram(text: str) -> bool:
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        log("WARNING: BOT_TOKEN / CHAT_ID not configured - skipping Telegram send.")
        return False

    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id":    CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
    }).encode()

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                log("Telegram message sent OK.")
                return True
            else:
                log(f"Telegram API error: {result}")
                return False
    except Exception as e:
        log(f"Failed to send Telegram message: {e}")
        return False


def read_timestamp():
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        ts   = root.attrib.get("TimeStamp")
        return int(ts) if ts else None
    except FileNotFoundError:
        log("XML file not found.")
        return None
    except ET.ParseError as e:
        log(f"XML parse error: {e}")
        return None
    except Exception as e:
        log(f"Unexpected error reading XML: {e}")
        return None


def main():
    log("=" * 55)
    log(f"  {SERVER_NAME} - Monitor starting")
    log(f"  XML  : {XML_PATH}")
    log(f"  Stale threshold : {STALE_THRESHOLD}s")
    log(f"  Check interval  : {CHECK_INTERVAL}s")
    log("=" * 55)

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        log("WARNING: BOT_TOKEN is not set - alerts will NOT be sent to Telegram!")

    last_timestamp   = None
    last_change_time = None
    server_was_up    = True
    first_run        = True

    while True:
        now = time.time()
        ts  = read_timestamp()

        if first_run:
            if ts is not None:
                last_timestamp   = ts
                last_change_time = now
                server_was_up    = True
                log(f"Server is ONLINE  |  timestamp={ts}")
            else:
                last_change_time = now
                server_was_up    = False
                log("Server appears OFFLINE at startup (XML unreadable).")
            first_run = False

        elif ts is None:
            if server_was_up:
                server_was_up = False
                log("Server went OFFLINE (XML file missing / unreadable).")
                send_telegram(
                    f"<b>{SERVER_NAME}</b>\n\n"
                    f"Server is <b>OFFLINE</b>\n"
                    f"(XML file missing or unreadable)\n\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

        elif ts != last_timestamp:
            if not server_was_up:
                log(f"Server is back ONLINE  |  timestamp={ts}")
                send_telegram(
                    f"<b>{SERVER_NAME}</b>\n\n"
                    f"Server is back <b>ONLINE</b>\n\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                server_was_up = True

            last_timestamp   = ts
            last_change_time = now

        else:
            stale_seconds = now - last_change_time

            if stale_seconds >= STALE_THRESHOLD and server_was_up:
                server_was_up = False
                log(f"Server went OFFLINE (timestamp frozen for {int(stale_seconds)}s).")
                send_telegram(
                    f"<b>{SERVER_NAME}</b>\n\n"
                    f"Server is <b>OFFLINE</b>\n"
                    f"(No update for {int(stale_seconds)} seconds)\n\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            else:
                status = "ONLINE" if server_was_up else "OFFLINE"
                log(f"{status}  |  timestamp={ts}  |  stale={int(stale_seconds)}s")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nMonitor stopped by user.")
        sys.exit(0)
