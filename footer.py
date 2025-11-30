
from __future__ import annotations

import subprocess
import time
from typing import Dict, Optional, Tuple

import pygame

# Colors are shared by the footer ticker and intentionally kept module-level for reuse.
BLUE: Tuple[int, int, int] = (0, 160, 255)


def _safe_check_output(cmd) -> str:
    """Return stripped command output, swallowing any error."""

    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

def _get_ip_address():
    out = _safe_check_output(["hostname", "-I"])
    return out.split()[0] if out else "IP N/A"

def _get_public_ip():
    for cmd in (
        ["curl", "-m", "2", "-s", "https://api.ipify.org"],
        ["curl", "-m", "2", "-s", "https://ifconfig.me"],
    ):
        out = _safe_check_output(cmd)
        if out:
            return out
    return "N/A"

def _get_pi_model():
    try:
        with open("/proc/device-tree/model", "rb") as f:
            raw = f.read().replace(b"\x00", b"")
        return raw.decode("utf-8", "ignore").strip()
    except Exception:
        return "UNKNOWN MODEL"

def _get_os_version():
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        return "UNKNOWN OS"
    return "UNKNOWN OS"

def _get_geo():
    out = _safe_check_output(["curl", "-s", "-m", "2", "ipinfo.io/loc"])
    return out.replace("\x00", "") if out else "UNKNOWN"

def _get_local_time():
    return time.strftime("%H:%M:%S %Z")

def _build_ticker_text(state: Dict[str, str]) -> str:
    parts = [
        f"VERSION {state.get('version', 'N/A')}",
        f"LAN {state.get('lan_ip', 'N/A')}",
        f"PUBLIC {state.get('public_ip', 'N/A')}",
        f"MODEL {state.get('model', 'N/A')}",
        f"OS {state.get('os', 'N/A')}",
        f"LOC {state.get('geo', 'N/A')}",
        f"TIME {state.get('time', 'N/A')}",
    ]
    base = "  |  ".join(parts)
    base = base.replace("\x00", "")
    return base.upper() + "   •   "

def init_footer_state(version: Optional[str] = None) -> Dict[str, str]:
    """Initialize footer state with system info.

    Args:
        version: Optional version label to include at the start of the ticker.
    """
    now = time.time()
    state = {
        "version": version or "N/A",
        "lan_ip": _get_ip_address(),
        "public_ip": _get_public_ip(),
        "model": _get_pi_model(),
        "os": _get_os_version(),
        "geo": _get_geo(),
        "time": _get_local_time(),
        "last_refresh": now,
        "_last_rendered_text": "",
        "_last_rendered_surface": None,
    }
    state["ticker_text"] = _build_ticker_text(state)
    return state

def _refresh_state(state: Dict[str, str], dynamic_interval: float = 7.0) -> bool:
    """Refresh dynamic fields in the footer state.

    Returns True if any displayed field changed (so the ticker surface should be rerendered).
    """

    now = time.time()
    last = float(state.get("last_refresh", 0.0))
    changed = False

    if now - last >= dynamic_interval:
        state["public_ip"] = _get_public_ip()
        state["geo"] = _get_geo()
        state["last_refresh"] = now
        changed = True

    new_time = _get_local_time()
    if new_time != state.get("time"):
        state["time"] = new_time
        changed = True

    if changed:
        state["ticker_text"] = _build_ticker_text(state)

    return changed


def _get_ticker_surface(state: Dict[str, str], footer_font: pygame.font.Font) -> Optional[pygame.Surface]:
    """Return a cached ticker surface, rerendering only when the text changes."""

    ticker = state.get("ticker_text", "")
    if not ticker:
        return None

    last_text = state.get("_last_rendered_text", "")
    surface: Optional[pygame.Surface] = state.get("_last_rendered_surface")  # type: ignore[assignment]

    if ticker != last_text or surface is None:
        surface = footer_font.render(ticker, True, BLUE)
        state["_last_rendered_text"] = ticker
        state["_last_rendered_surface"] = surface

    return surface

def draw_footer(
    screen: pygame.Surface,
    footer_font: pygame.font.Font,
    state: Dict[str, str],
    ticker_x: float,
    screen_width: int,
    screen_height: int,
    tick_speed: float = 2.0,
) -> float:
    """Draw the scrolling footer ticker.

    Returns the updated ticker_x position.
    Does NOT call display.update().
    """

    changed = _refresh_state(state)
    surf = _get_ticker_surface(state, footer_font)
    if surf is None:
        return ticker_x

    # Recompute width on rerender only.
    width = surf.get_width()
    x = int(ticker_x)
    y = screen_height - 18
    screen.blit(surf, (x, y))

    # Wrap-around logic
    x -= tick_speed
    if x < -width:
        x = screen_width

    # Keep cached surface in sync if text changed mid-frame (e.g., during slow renders).
    if changed:
        state["_last_rendered_surface"] = surf

    return float(x)
