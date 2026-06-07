"""BLE ⇄ Redis sidecar for the physical Lego rovers.

Owner: Person 3 (Hardware Rover + Gemma Edge)

Runs on the Mac (the BLE *central*) and bridges each Lego hub into the rest of
the system over Redis — no extra HTTP gateway needed. It speaks the same
`redis_layer` the backend already uses:

  * Telemetry  (hub -> backend):  every '\\n'-terminated line the hub notifies
    over the Nordic-UART TX characteristic is pushed to the Redis list
    ``{rover_id}:telemetry`` (newest first, capped) and published live on the
    ``{rover_id}:telemetry`` channel.
  * Commands   (backend -> hub):  the backend / HardwareRover enqueues commands
    with ``client.lpush("{rover_id}:commands", cmd)`` where ``cmd`` is a plain
    string ("FWD:20") or a ``{"command": "FWD:20"}`` dict. The sidecar pops them
    FIFO (BRPOP) and writes them to the hub's Nordic-UART RX characteristic.

Robot labels map to the canonical rover ids (config.ROVER_IDS) used everywhere:
    robot alpha -> rover1
    robot beta  -> rover2

Usage (from the backend/ directory, with the project venv active):
    python ble_sidecar.py          # connect every hub that has an address set
    python ble_sidecar.py scan     # just scan and print nearby BLE devices

Configure addresses in .env:  BLE_ALPHA_ADDRESS / BLE_BETA_ADDRESS
(on macOS these are CoreBluetooth UUIDs, not MAC addresses — use ``scan`` to
discover them, then paste the right one into .env).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time

from bleak import BleakClient, BleakScanner
from dotenv import load_dotenv

# Import the Redis client module under an alias so it never clashes with the
# BleakClient instance we name `ble` below.
from redis_layer import client as redis_client
from redis_layer.client import get_redis

# redis_layer.client already loads .env via config, but be explicit so the
# sidecar also works when run fully standalone.
load_dotenv()

log = logging.getLogger("roverswarm.ble_sidecar")

# Nordic UART Service — the service Pybricks / most BLE-UART hubs expose.
# RX = central -> hub (we write here);  TX = hub -> central (we subscribe here).
UART_RX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_TX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Physical robot -> canonical rover id (rover1/rover2). Alpha = rover1.
ROVERS: dict[str, dict] = {
    "rover1": {"label": "alpha", "address": os.getenv("BLE_ALPHA_ADDRESS", "").strip()},
    "rover2": {"label": "beta", "address": os.getenv("BLE_BETA_ADDRESS", "").strip()},
}

# Target the hub should seek; sent on connect. (A plain handshake value — the
# hub firmware decides what to do with it.)
MISSION_COLOR = os.getenv("MISSION_COLOR", "RED").upper()

MAX_TELEMETRY = 200          # cap the per-rover telemetry list
RECONNECT_MAX_BACKOFF = 30   # seconds between reconnect attempts (capped)
COMMAND_POP_TIMEOUT = 1      # BRPOP timeout so we re-check the BLE link each second


def _commands_key(rover_id: str) -> str:
    return f"{rover_id}:commands"


def _telemetry_key(rover_id: str) -> str:
    return f"{rover_id}:telemetry"


def _parse_command(raw) -> str | None:
    """Accept a plain-string command or a {'command': ...} JSON payload."""
    if raw is None:
        return None
    value = raw
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8", errors="ignore")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass  # not JSON — treat as a bare command string
    if isinstance(value, dict):
        value = value.get("command")
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return None


async def _write_line(ble: BleakClient, text: str) -> None:
    """Write one newline-terminated line to the hub's RX characteristic."""
    payload = (text.rstrip("\n") + "\n").encode("utf-8")
    await ble.write_gatt_char(UART_RX, payload, response=False)


async def _store_telemetry(rover_id: str, raw_line: str) -> None:
    """Persist + broadcast one telemetry line (graceful if Redis is down)."""
    entry = {"ts": time.time(), "raw": raw_line}
    await redis_client.lpush(_telemetry_key(rover_id), entry)
    try:  # trimming is best-effort; never let it kill the loop
        await get_redis().ltrim(_telemetry_key(rover_id), 0, MAX_TELEMETRY - 1)
    except Exception as exc:  # noqa: BLE001
        log.debug("[%s] ltrim failed: %s", rover_id, exc)
    await redis_client.publish(_telemetry_key(rover_id), entry)
    # Extension point [Person 3]: parse structured lines here (e.g. "POS:x,y,h"
    # -> rover_state.set_position, "ERR:..." -> rover_state.log_error) once those
    # redis_layer functions are implemented.


async def _telemetry_consumer(rover_id: str, queue: "asyncio.Queue[str]") -> None:
    """Drain buffered telemetry lines into Redis (runs until cancelled)."""
    while True:
        line = await queue.get()
        log.info("[%s] hub: %s", rover_id, line)
        await _store_telemetry(rover_id, line)


async def _command_consumer(rover_id: str, ble: BleakClient) -> None:
    """FIFO-pop commands from Redis and write them to the hub while connected."""
    key = _commands_key(rover_id)
    while ble.is_connected:
        try:
            popped = await get_redis().brpop(key, timeout=COMMAND_POP_TIMEOUT)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — Redis hiccup; back off and retry
            log.warning("[%s] command pop failed: %s", rover_id, exc)
            await asyncio.sleep(1)
            continue
        if not popped:
            continue  # BRPOP timeout — loop to re-check the BLE link
        _key, raw = popped
        cmd = _parse_command(raw)
        if cmd and ble.is_connected:
            log.info("[%s] -> %s", rover_id, cmd)
            await _write_line(ble, cmd)


async def _monitor(ble: BleakClient) -> None:
    """Complete as soon as the BLE link drops, so we can reconnect."""
    while ble.is_connected:
        await asyncio.sleep(0.5)


async def connect_hub(rover_id: str, info: dict) -> None:
    """Maintain a connection to one hub forever, reconnecting with backoff."""
    label = info["label"]
    address = info["address"]
    backoff = 1
    while True:
        try:
            log.info("[%s/%s] connecting to %s ...", rover_id, label, address)
            async with BleakClient(address, timeout=15) as ble:
                log.info("[%s/%s] connected.", rover_id, label)
                backoff = 1

                loop = asyncio.get_running_loop()
                queue: "asyncio.Queue[str]" = asyncio.Queue()
                line_buf = ""

                def on_notify(_sender, data: bytearray) -> None:
                    # Runs on the BLE thread; hand lines to the loop thread-safely.
                    nonlocal line_buf
                    line_buf += data.decode("utf-8", errors="ignore")
                    while "\n" in line_buf:
                        line, line_buf = line_buf.split("\n", 1)
                        line = line.strip()
                        if line:
                            loop.call_soon_threadsafe(queue.put_nowait, line)

                await ble.start_notify(UART_TX, on_notify)
                # Handshake: identify the rover + tell the hub what to seek.
                await _write_line(ble, f"ID:{label.upper()}")
                await _write_line(ble, f"TARGET:{MISSION_COLOR}")

                tasks = [
                    asyncio.create_task(_telemetry_consumer(rover_id, queue)),
                    asyncio.create_task(_command_consumer(rover_id, ble)),
                    asyncio.create_task(_monitor(ble)),
                ]
                try:
                    done, _pending = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                finally:
                    for t in tasks:
                        t.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    try:
                        if ble.is_connected:
                            await ble.stop_notify(UART_TX)
                    except Exception:  # noqa: BLE001 — already tearing down
                        pass

                for t in done:
                    if not t.cancelled() and t.exception():
                        log.warning("[%s/%s] task ended: %s", rover_id, label, t.exception())
            log.warning("[%s/%s] disconnected.", rover_id, label)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — connect failure / dropped link
            log.warning(
                "[%s/%s] connection error: %s — retry in %ss",
                rover_id, label, exc, backoff,
            )

        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, RECONNECT_MAX_BACKOFF)


async def scan() -> None:
    """Discover and print nearby BLE devices (to find a hub's address)."""
    log.info("scanning for BLE devices (10s) ...")
    devices = await BleakScanner.discover(timeout=10)
    if not devices:
        log.info("no BLE devices found.")
        return
    for d in devices:
        log.info("  %s   %s", d.address, d.name or "(unknown)")


async def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "scan":
        await scan()
        return

    configured = {rid: info for rid, info in ROVERS.items() if info["address"]}
    if not configured:
        log.warning(
            "No BLE addresses set (BLE_ALPHA_ADDRESS / BLE_BETA_ADDRESS). "
            "Scanning so you can find them — copy the right address into .env."
        )
        await scan()
        return

    log.info("starting BLE sidecar for: %s", ", ".join(configured))
    try:
        await asyncio.gather(*(connect_hub(rid, info) for rid, info in configured.items()))
    finally:
        await redis_client.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("sidecar stopped.")
