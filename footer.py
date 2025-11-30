
import subprocess
import time
import pygame

BLUE = (0, 160, 255)

def _safe_check_output(cmd):
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
        out = _safe_check_output(["grep", "PRETTY_NAME", "/etc/os-release"])
        return out.split("=", 1)[1].strip().replace('"', "")
    except Exception:
        return "UNKNOWN OS"

def _get_geo():
    out = _safe_check_output(["curl", "-s", "-m", "2", "ipinfo.io/loc"])
    return out.replace("\x00", "") if out else "UNKNOWN"

def _get_local_time():
    return time.strftime("%H:%M:%S %Z")

def _build_ticker_text(state: dict) -> str:
    parts = [
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

def init_footer_state() -> dict:
    """Initialize footer state with system info."""
    now = time.time()
    state = {
        "lan_ip": _get_ip_address(),
        "public_ip": _get_public_ip(),
        "model": _get_pi_model(),
        "os": _get_os_version(),
        "geo": _get_geo(),
        "time": _get_local_time(),
        "last_refresh": now,
    }
    state["ticker_text"] = _build_ticker_text(state)
    return state

def _refresh_state(state: dict, dynamic_interval: float = 7.0) -> dict:
    """Refresh dynamic fields in the footer state.
    - public_ip & geo: every dynamic_interval seconds
    - time: every call
    """
    now = time.time()
    last = state.get("last_refresh", 0.0)

    if now - last >= dynamic_interval:
        state["public_ip"] = _get_public_ip()
        state["geo"] = _get_geo()
        state["last_refresh"] = now

    state["time"] = _get_local_time()
    state["ticker_text"] = _build_ticker_text(state)
    return state

def draw_footer(
    screen: pygame.Surface,
    footer_font: pygame.font.Font,
    state: dict,
    ticker_x: float,
    screen_width: int,
    screen_height: int,
    tick_speed: float = 1.0,
) -> float:
    """Draw the scrolling footer ticker.
    Returns the updated ticker_x position.
    Does NOT call display.update().
    """
    state = _refresh_state(state)

    ticker = state.get("ticker_text", "")
    if not ticker:
        return ticker_x

    surf = footer_font.render(ticker, True, BLUE)
    width = surf.get_width()

    x = int(ticker_x)
    y = screen_height - 18
    screen.blit(surf, (x, y))

    # Wrap-around logic
    x -= tick_speed
    if x < -width:
        x = screen_width

    return float(x)
