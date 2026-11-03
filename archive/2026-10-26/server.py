import os
import json
import logging
import ipaddress
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("family-tv")

app = FastAPI(title="Family TV")

WEB_DIR = Path("/app/web")
TV_HOST = os.getenv("VIZIO_HOST", "192.168.50.29")
TV_TOKEN = os.getenv("VIZIO_TOKEN", "")

# Only allow requests to the configured TV.
try:
    ipaddress.ip_address(TV_HOST)
except ValueError:
    raise RuntimeError("VIZIO_HOST must be an IP address")

TV_URL = f"https://{TV_HOST}:7345"


class LaunchRequest(BaseModel):
    catalog_id: str = Field(min_length=1, max_length=20)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "tv_configured": bool(TV_TOKEN),
    }


def load_catalog():
    path = WEB_DIR / "apps.json"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.error("Catalog unavailable: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Application catalog unavailable",
        )

    if not isinstance(data, list):
        raise HTTPException(
            status_code=500,
            detail="Invalid application catalog",
        )

    return data


@app.post("/api/launch")
async def launch_application(request: LaunchRequest):
    if not TV_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="TV authentication not configured",
        )

    catalog = load_catalog()

    # The browser sends only a catalog ID.
    # The server determines the actual launch configuration.
    application = next(
        (
            item for item in catalog
            if str(item.get("id")) == request.catalog_id
        ),
        None,
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    try:
        app_id = str(application["app_id"])
        namespace = int(application["name_space"])
        message = application.get("message") or ""
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=500,
            detail="Invalid application configuration",
        )

    payload = {
        "VALUE": {
            "MESSAGE": message,
            "NAME_SPACE": namespace,
            "APP_ID": app_id,
        }
    }

    headers = {
        "AUTH": TV_TOKEN,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            verify=False,
            timeout=10.0,
            trust_env=False,
        ) as client:
            response = await client.put(
                f"{TV_URL}/app/launch",
                json=payload,
                headers=headers,
            )

        response.raise_for_status()
        result = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        logger.error("TV launch request failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with Vizio TV",
        )

    if result.get("STATUS", {}).get("RESULT") != "SUCCESS":
        logger.warning("TV rejected launch request")
        raise HTTPException(
            status_code=502,
            detail="Vizio rejected application launch",
        )

    logger.info("Launched catalog application: %s", request.catalog_id)

    return {
        "success": True,
        "application": application.get("name"),
    }


@app.get("/")
async def home():
    return FileResponse(WEB_DIR / "index.html")


# Serve app icons/catalog and other static files.
# Registered last so API routes take precedence.
app.mount(
    "/",
    StaticFiles(directory=str(WEB_DIR)),
    name="web",
)
