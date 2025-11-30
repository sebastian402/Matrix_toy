
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pygame

from footer import draw_footer, init_footer_state
from header import draw_header
from matrix_movie_singleline import LINES

# Screen / UI
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320

BLACK: Tuple[int, int, int] = (0, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
DIM_WHITE: Tuple[int, int, int] = (120, 120, 120)
BLUE: Tuple[int, int, int] = (0, 160, 255)

SCAN_INTERVAL = 21       # seconds between scans
TICKER_SPEED  = 1        # pixels per frame
MOVIE_TYPE_DELAY = 0.05  # seconds per character for movie line typing

BASE_DIR = Path(__file__).resolve().parent
DISCOVERED_FILE = BASE_DIR / "discovered_devices.json"
LAB_FILE = BASE_DIR / "lab_devices.json"

ROW_Y_START = 56   # start of network rows
ROW_H       = 20   # row height (for bigger text)

# Title text (animated)
TITLE_TEXT    = "~/MATRIX PROXIMITY NET SCAN//"
VERSION_TEXT  = "v0.1.0"

# ---------- JSON helpers ----------

def load_json(path: Path, default):
    """Load JSON data from *path*, returning *default* on any failure."""

    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: Path, data) -> None:
    """Atomically save JSON data to *path* using a temporary file."""

    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

# ---------- WiFi scan & lab state ----------

def _safe_check_output(cmd) -> str:
    """Return decoded output for *cmd* or an empty string on failure."""

    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def scan_nmcli() -> List[Dict[str, object]]:
    """Scan Wi-Fi networks using nmcli and return sorted network dictionaries."""
    try:
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,BSSID", "dev", "wifi"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return []

    nets: List[Dict[str, object]] = []
    for line in out.splitlines():
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        ssid, signal, sec, bssid = parts
        ssid = ssid if ssid else "<hidden>"
        sec = sec if sec else "OPEN"
        try:
            sig = int(signal)
        except Exception:
            sig = 0
        nets.append(
            {
                "ssid": ssid,
                "signal": sig,
                "security": sec,
                "bssid": bssid,
            }
        )

    nets.sort(key=lambda x: x["signal"], reverse=True)
    return nets

def update_discovered(discovered: Dict[str, Dict[str, object]], nets: List[Dict[str, object]]):
    now = datetime.utcnow().isoformat() + "Z"
    for n in nets:
        bssid = n.get("bssid")
        if not bssid:
            continue
        if bssid not in discovered:
            discovered[bssid] = {
                "ssid": n["ssid"],
                "first_seen": now,
                "last_seen": now,
                "last_signal": n["signal"],
                "security": n["security"],
            }
        else:
            discovered[bssid]["ssid"] = n["ssid"]
            discovered[bssid]["last_seen"] = now
            discovered[bssid]["last_signal"] = n["signal"]
            discovered[bssid]["security"] = n["security"]
    return discovered

def ensure_lab_entries(discovered: Dict[str, Dict[str, object]], lab_devices: Dict[str, Dict[str, object]]):
    changed = False
    for bssid, info in discovered.items():
        if bssid not in lab_devices:
            lab_devices[bssid] = {
                "ssid": info.get("ssid", ""),
                "active": False,
            }
            changed = True
    if changed:
        save_json(LAB_FILE, lab_devices)
    return lab_devices

def toggle_lab_device(
    bssid: str, discovered: Dict[str, Dict[str, object]], lab_devices: Dict[str, Dict[str, object]]
):
    info = discovered.get(bssid, {})
    entry = lab_devices.get(
        bssid,
        {"ssid": info.get("ssid", ""), "active": False},
    )
    entry["active"] = not entry.get("active", False)
    lab_devices[bssid] = entry
    save_json(LAB_FILE, lab_devices)
    print(f"[LAB] Toggled {bssid}: active={entry['active']}")
    return lab_devices

# ---------- Drawing helpers ----------

def sig_color(sig: int) -> Tuple[int, int, int]:
    s = max(0, min(100, sig)) / 100.0
    g = int(80 + 175 * s)
    return (0, g, 0)

def sig_level(sig: int) -> int:
    if sig >= 80:
        return 4
    if sig >= 60:
        return 3
    if sig >= 40:
        return 2
    if sig >= 20:
        return 1
    return 0

def draw_bars(screen: pygame.Surface, x: int, y: int, sig: int, color: Tuple[int, int, int]) -> None:
    level = sig_level(sig)
    w = 4
    space = 1
    hmax = 12
    for i in range(4):
        h = hmax * (i + 1) // 4
        bx = x + i * (w + space)
        by = y + (hmax - h)
        pygame.draw.rect(
            screen,
            color if i < level else DIM_WHITE,
            (bx, by, w, h),
        )

def get_movie_line() -> str:
    return random.choice(LINES)

def draw_console(
    screen: pygame.Surface,
    header_font: pygame.font.Font,
    row_font: pygame.font.Font,
    footer_font: pygame.font.Font,
    nets: List[Dict[str, object]],
    discovered: Dict[str, Dict[str, object]],
    lab_devices: Dict[str, Dict[str, object]],
    movie_line: str,
    movie_visible_len: int,
    remaining: float,
    ticker_x: float,
    cycle_start_time: float,
    scanning: bool,
    footer_state: Dict[str, str],
) -> Tuple[float, Dict[int, str]]:
    """Draw the entire console frame and return (ticker_x, row_map)."""
    screen.fill(BLACK)
    now = time.time()

    # ----- HEADER (title + countdown) -----
    draw_header(
        screen=screen,
        header_font=header_font,
        now=now,
        cycle_start_time=cycle_start_time,
        scanning=scanning,
        remaining=remaining,
        scan_interval=SCAN_INTERVAL,
        title_text=TITLE_TEXT,
        screen_width=SCREEN_WIDTH,
        version_text=VERSION_TEXT,
    )

    # ----- Movie line under the title -----
    visible_text = (
        movie_line[:movie_visible_len]
        if movie_visible_len <= len(movie_line)
        else movie_line
    )
    movie_surf = row_font.render(visible_text, True, (0, 120, 255))
    screen.blit(movie_surf, (10, 30))

    # Draw movie-line cursor (white square) blinking
    if int(time.time() * 2) % 2 == 0:
        cursor_size = row_font.get_height() - 4
        cursor_x = 10 + movie_surf.get_width() + 4
        cursor_y = 30 + 2
        pygame.draw.rect(
            screen,
            WHITE,
            (cursor_x, cursor_y, cursor_size, cursor_size),
        )

    # ----- separator line between header and table -----
    sep_top_y = ROW_Y_START - 6
    pygame.draw.line(
        screen,
        DIM_WHITE,
        (6, sep_top_y),
        (SCREEN_WIDTH - 6, sep_top_y),
        1,
    )

    # ----- Wi-Fi table -----
    COL_SSID = 10
    COL_SEC = 190
    COL_SIG = 270
    COL_LAB = 355

    y = ROW_Y_START
    max_rows = (SCREEN_HEIGHT - ROW_Y_START - 26) // ROW_H
    row_map = {}

    for idx, n in enumerate(nets[:max_rows]):
        ssid = n["ssid"][:18]
        sig = n["signal"]
        sec = n["security"][:4]
        bssid = n.get("bssid", "")

        base_color = sig_color(sig)
        lab_active = bssid in lab_devices and lab_devices[bssid].get("active", False)

        text_color = (
            (0, max(base_color[1], 240), 0) if lab_active else base_color
        )

        screen.blit(row_font.render(ssid, True, text_color), (COL_SSID, y))
        screen.blit(row_font.render(sec, True, text_color), (COL_SEC, y))

        draw_bars(screen, COL_SIG, y, sig, text_color)
        screen.blit(
            row_font.render(f"{sig:3d}%", True, text_color),
            (COL_SIG + 24, y),
        )

        lab_flag = "✔" if lab_active else ""
        screen.blit(row_font.render(lab_flag, True, text_color), (COL_LAB, y))

        if bssid:
            row_map[idx] = bssid

        y += ROW_H

    # ----- separator line above footer -----
    sep_bot_y = SCREEN_HEIGHT - 22
    pygame.draw.line(
        screen,
        DIM_WHITE,
        (6, sep_bot_y),
        (SCREEN_WIDTH - 6, sep_bot_y),
        1,
    )

    # ----- FOOTER ticker -----
    ticker_x = draw_footer(
        screen=screen,
        footer_font=footer_font,
        state=footer_state,
        ticker_x=ticker_x,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        tick_speed=TICKER_SPEED,
    )

    pygame.display.update()
    return ticker_x, row_map

# ---------- Main loop ----------

def main():
    pygame.init()
    pygame.font.init()

    header_font = pygame.font.SysFont("dejavusansmono", 12, bold=True)
    row_font = pygame.font.SysFont("dejavusansmono", 12)
    # Footer font same size as title for readability
    footer_font = pygame.font.SysFont("dejavusansmono", 12)

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.FULLSCREEN,
    )
    pygame.mouse.set_visible(True)

    discovered = load_json(DISCOVERED_FILE, {})
    lab_devices = load_json(LAB_FILE, {})

    # Initial scan
    nets = scan_nmcli()
    discovered = update_discovered(discovered, nets)
    save_json(DISCOVERED_FILE, discovered)
    lab_devices = ensure_lab_entries(discovered, lab_devices)

    cycle_start = time.time()
    scanning = False
    scanning_until = 0.0
    ticker_x = float(SCREEN_WIDTH)
    footer_state = init_footer_state()

    current_movie_line = get_movie_line()
    movie_visible_len = 0
    last_movie_type_time = time.time()

    clock = pygame.time.Clock()
    running = True
    row_map = {}

    while running:
        now = time.time()

        # Typing animation for movie line
        if movie_visible_len < len(current_movie_line):
            if now - last_movie_type_time >= MOVIE_TYPE_DELAY:
                movie_visible_len += 1
                last_movie_type_time = now

        # Scan timing
        if scanning:
            remaining = 0.0
            if now >= scanning_until:
                nets = scan_nmcli()
                discovered = update_discovered(discovered, nets)
                save_json(DISCOVERED_FILE, discovered)
                lab_devices = ensure_lab_entries(discovered, lab_devices)

                cycle_start = time.time()
                scanning = False

                # pick new movie line after each scan
                current_movie_line = get_movie_line()
                movie_visible_len = 0
                last_movie_type_time = now
        else:
            elapsed = now - cycle_start
            remaining = SCAN_INTERVAL - elapsed
            if remaining <= 0.0:
                scanning = True
                scanning_until = now + 1.0
                remaining = 0.0

        # Draw everything
        ticker_x, row_map = draw_console(
            screen=screen,
            header_font=header_font,
            row_font=row_font,
            footer_font=footer_font,
            nets=nets,
            discovered=discovered,
            lab_devices=lab_devices,
            movie_line=current_movie_line,
            movie_visible_len=movie_visible_len,
            remaining=remaining,
            ticker_x=ticker_x,
            cycle_start_time=cycle_start,
            scanning=scanning,
            footer_state=footer_state,
        )

        # Handle events
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif e.key == pygame.K_r:
                    nets = scan_nmcli()
                    discovered = update_discovered(discovered, nets)
                    save_json(DISCOVERED_FILE, discovered)
                    lab_devices = ensure_lab_entries(discovered, lab_devices)
                    cycle_start = time.time()
                    scanning = False
                    scanning_until = 0.0

                    current_movie_line = get_movie_line()
                    movie_visible_len = 0
                    last_movie_type_time = time.time()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                if ROW_Y_START <= y < SCREEN_HEIGHT - 26:
                    row_index = (y - ROW_Y_START) // ROW_H
                    bssid = row_map.get(row_index)
                    if bssid:
                        lab_devices = toggle_lab_device(
                            bssid, discovered, lab_devices
                        )

        clock.tick(20)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
