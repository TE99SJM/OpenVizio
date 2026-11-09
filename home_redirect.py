
import asyncio
import logging
import os
import time

import httpx

# --------------------------------------------------
# Family TV — Automatic Home Redirect
# Vizio V505-H1 / MT5691
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Reduce unnecessary HTTP request logging.
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger("family-tv-redirect")

TV_HOST = os.environ["VIZIO_HOST"]
TV_TOKEN = os.environ["VIZIO_TOKEN"]

TV_URL = f"https://{TV_HOST}:7345"

FAMILY_URL = os.getenv(
    "FAMILY_TV_URL",
    "http://192.0.2.20:3040/"
)

POLL_SECONDS = 2
REDIRECT_COOLDOWN = 15
VERIFY_DELAY = 3

last_redirect = 0.0


# --------------------------------------------------
# API helpers
# --------------------------------------------------

async def get_json(client, endpoint):
    response = await client.get(
        TV_URL + endpoint,
        headers={"AUTH": TV_TOKEN}
    )

    response.raise_for_status()
    return response.json()


async def get_current_app(client):
    result = await get_json(client, "/app/current")

    if result.get("STATUS", {}).get("RESULT") != "SUCCESS":
        return None

    return result.get("ITEM", {}).get("VALUE", {})


# --------------------------------------------------
# Application identification
# --------------------------------------------------

def identify_application(current):
    if not isinstance(current, dict):
        return "unknown"

    app_id = str(current.get("APP_ID", ""))
    namespace = current.get("NAME_SPACE")
    message = current.get("MESSAGE", "")

    try:
        namespace = int(namespace)
    except (TypeError, ValueError):
        return "unknown"

    # Our custom Family TV launcher.
    if app_id == "17" and namespace == 4:
        if message == FAMILY_URL:
            return "family_tv"

        # Same launch identity, different URL.
        # Do not override an unrelated page.
        return "other"

    # APP_ID 1 / namespace 5 is ambiguous and also used by YouTube.
    # Do not redirect it: preserve native phone casting.
    if app_id == "1" and namespace == 5:
        return "other"

    # Vizio Home, representation 2.
    if app_id == "1" and namespace == 4:
        if isinstance(message, str) and "bundles/home" in message:
            return "vizio_home"

    return "other"


# --------------------------------------------------
# Launch Family TV
# --------------------------------------------------

async def launch_family_tv(client):
    payload = {
        "VALUE": {
            "MESSAGE": FAMILY_URL,
            "NAME_SPACE": 4,
            "APP_ID": "17"
        }
    }

    response = await client.put(
        TV_URL + "/app/launch",
        headers={
            "AUTH": TV_TOKEN,
            "Content-Type": "application/json"
        },
        json=payload
    )

    response.raise_for_status()

    result = response.json()

    return (
        result.get("STATUS", {}).get("RESULT")
        == "SUCCESS"
    )


# --------------------------------------------------
# Main monitor
# --------------------------------------------------

async def monitor():
    global last_redirect

    log.info("Family TV Home redirect monitor starting")
    log.info("Target URL: %s", FAMILY_URL)
    log.info("Polling interval: %s seconds", POLL_SECONDS)

    last_state = None

    async with httpx.AsyncClient(
        verify=False,
        timeout=8,
        trust_env=False
    ) as client:

        while True:
            try:
                current = await get_current_app(client)

                if current is None:
                    await asyncio.sleep(POLL_SECONDS)
                    continue

                state = identify_application(current)

                # Only log changes, not every poll.
                if state != last_state:
                    log.info("Detected application: %s", state)
                    last_state = state

                # Never interrupt applications other
                # than the identified Vizio Home.
                if state != "vizio_home":
                    await asyncio.sleep(POLL_SECONDS)
                    continue

                elapsed = time.monotonic() - last_redirect

                if elapsed < REDIRECT_COOLDOWN:
                    await asyncio.sleep(POLL_SECONDS)
                    continue

                log.info("Original Vizio Home detected")

                # Apply cooldown before attempting launch.
                last_redirect = time.monotonic()

                success = await launch_family_tv(client)

                if not success:
                    log.warning("Vizio rejected launch request")
                    await asyncio.sleep(POLL_SECONDS)
                    continue

                log.info("Launch request accepted")

                # Allow the TV to finish switching screens.
                await asyncio.sleep(VERIFY_DELAY)

                verified = await get_current_app(client)
                verified_state = identify_application(verified)

                if verified_state == "family_tv":
                    log.info("SUCCESS: Family TV is now active")
                    last_state = "family_tv"
                else:
                    log.warning(
                        "Redirect not confirmed. Current state: %s",
                        verified_state
                    )
                    last_state = verified_state

            except asyncio.CancelledError:
                raise

            except Exception as error:
                log.warning(
                    "Monitor error: %s",
                    type(error).__name__
                )

            await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        log.info("Home redirect monitor stopped")
