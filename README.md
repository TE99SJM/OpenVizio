# OpenVizio

A simple, self-hosted home screen for Vizio SmartCast TVs, developed from the Family TV project. OpenVizio aims to provide large app tiles and a menu that is easy to navigate with a TV remote.

This is an independent project, not affiliated with or endorsed by Vizio. It runs alongside the TV's existing software; it does not replace or rewrite firmware.

## Current status

**Partial source recovery. This repository is not yet a complete installable release.**

The Python files under `archive/2026-10-26/` are historical source snapshots recovered from an October 26, 2026 project paste. They are not a verified copy of the current deployment and have not been run or tested as part of this import.

The original paste contained both scripts consecutively. They were separated into their respective files and a trailing shell prompt was removed. No functional changes were made.

## Included files

| File | Purpose |
| --- | --- |
| `archive/2026-10-26/server.py` | Historical FastAPI backend for frontend hosting and catalog-based application launching. |
| `archive/2026-10-26/home_redirect.py` | Historical monitor intended to open the custom launcher when the TV's original Home screen is detected. |
| `.gitignore` | Excludes local environment files, credentials, logs, and Python runtime files. |

## Goals

- Large app tiles with remote arrow/select navigation.
- A configurable application catalog.
- Convenient access to TV inputs.
- A custom Home experience that cooperates with normal app playback and phone casting.

These are project goals; the recovered source does not establish that every feature is complete.

## Known issue

YouTube playback and phone casting have been reported to exit or return to the home screen in the existing project. Automatic Home redirection is a suspected cause, but the cause remains unconfirmed. No casting fix is included in this historical snapshot.

## Completing the source import

The following current files are still needed before installation can be documented and validated:

- Backend and Home redirect scripts.
- Dockerfile and Docker Compose configuration.
- Complete web frontend, app catalog, icons, and other assets.
- Dependency files and any startup scripts.
- A sanitized example configuration containing placeholders only.

Do not upload live environment files, pairing tokens, passwords, or private keys.

## Installation and validation

Installation instructions are pending the complete source import. The archived scripts alone are insufficient to build or run the application.

After import, validate container startup, remote navigation, app launching, input switching, Home behavior, and casting on a physical TV. Hardware behavior has not been verified by this repository import.

## License

No license has been selected. Public availability alone does not grant an open-source license.
