# OpenVizio

A simple, self-hosted home screen for Vizio SmartCast TVs. OpenVizio grew out of the Family TV project and provides large app tiles, remote navigation, and a customizable Home layout.

It runs on a separate Docker host and communicates with the TV over the local network. It does not replace TV firmware. OpenVizio is independent of, and not endorsed by, Vizio.

## Status

The current source has been imported from the supplied project archive. This is a prototype, developed for a Vizio V505-H1; compatibility with other models is unverified. The app and container retain the `Family TV` / `family-tv` names.

**Known YouTube conflict:** the included catalog identifies YouTube as app ID `1`, namespace `5`. The redirect monitor also classifies that exact identity as Vizio Home. It can therefore redirect away from YouTube. Phone casting interruptions have been reported. This import documents the conflict; it does not fix it. The monitor starts automatically with the backend, so consider this limitation before running the prototype.

## Features

- Large application tiles and an All Apps screen with search.
- Arrow/Select/Back remote navigation and mouse interaction.
- Show/hide, rename, and reorder Home tiles.
- Layout preferences saved in the current browser's local storage.
- A bundled catalog of 343 app entries with externally hosted icons.
- Server-side app launching and an automatic Home redirect monitor.

The catalog is a bundled snapshot, not a live discovery service or a guarantee that every listed app is installed, available, or launches on every TV. Live TV and HDMI tiles are currently placeholders: selecting them reports that input switching is not connected yet.

## Requirements

- Docker Engine with Docker Compose.
- A compatible Vizio SmartCast TV reachable from the Docker host.
- An existing TV pairing token. A pairing utility is not included.
- A host address reachable by the TV on port 3040.

## Setup

The example IP addresses below are documentation placeholders. Replace them with your own addresses.

1. Clone the repository:

   ```bash
   git clone https://github.com/TE99SJM/OpenVizio.git
   cd OpenVizio
   ```

2. Create a local configuration:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your TV IP, paired token, and the URL the TV can use to reach the Docker host:

   ```dotenv
   VIZIO_HOST=192.0.2.10
   VIZIO_TOKEN=replace_with_your_paired_tv_token
   FAMILY_TV_URL=http://192.0.2.20:3040/
   ```

   `VIZIO_HOST` must be an IP address. `FAMILY_TV_URL` must use a host address reachable from the TV, not localhost. Keep `.env` private.

3. Start the service, with the known YouTube limitation above in mind:

   ```bash
   docker compose up -d --build
   ```

4. Open `http://YOUR_SERVER_IP:3040/` in a browser to inspect the launcher. The redirect monitor attempts to open that page on the TV when it detects Home. Opening the page on a computer does not itself display it on the TV.

5. Check service health and logs:

   ```bash
   curl http://localhost:3040/api/health
   docker compose logs --tail=100 family-tv
   ```

   A healthy HTTP service does not prove TV connectivity, a valid pairing token, or correct Home detection.

## Usage

Use arrows and Select/OK to navigate. Open Customize Home to change tile visibility, names, and order. Use All Apps to search the bundled catalog. Back returns to the previous launcher screen.

Preferences are browser-specific. A desktop browser and the TV browser maintain separate layouts. Clearing browser storage resets the saved layout. App icons are loaded from external URLs and may be unavailable offline.

## Updating and stopping

After changing Python code or the Dockerfile:

```bash
docker compose up -d --build
```

The `web/` directory is mounted read-only into the container. Refresh the page after editing frontend files or the catalog. Recreate the service after changing `.env`:

```bash
docker compose up -d --force-recreate
```

To stop the service and its redirect monitor:

```bash
docker compose stop family-tv
```

Stopping it also stops the web launcher backend.

## Source layout

| Path | Purpose |
| --- | --- |
| `server.py` | FastAPI service and redirect task lifecycle. |
| `home_redirect.py` | Active-app polling and Home redirection. |
| `web/index.html` | Launcher UI, customization, and remote navigation. |
| `web/apps.json` | Bundled application catalog. |
| `Dockerfile` | Python 3.12 container and dependencies. |
| `docker-compose.yml` | Service, configuration, port, and frontend mount. |
| `.env.example` | Placeholder configuration. |
| `*.bak-20261026-212808` | Earlier files supplied in the archive; not used by the container. |
| `archive/2026-10-26/` | Earlier recovered Python snapshots; not used by the container. |

The supplied files were retained, with machine-specific default addresses replaced by documentation placeholders. Compose now reads the TV address and launcher URL from `.env`, along with the token. No playback or redirect logic was changed in this import.

## Validation

Import checks cover Python syntax, JavaScript syntax, JSON catalog structure and unique IDs, plus checks that Docker references the included source files. Docker build/start and physical TV behavior were not tested in this environment. Dependencies in the supplied Dockerfile are unpinned.

## License

No license has been selected. Public availability alone does not grant an open-source license. Third-party app names and externally hosted artwork belong to their respective owners.
