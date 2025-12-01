"""Animated Matrix-style header for the Wi-Fi console.

This module handles the title "dehashing" animation and the
color-shifting countdown indicator displayed at the top of the console.
It is intentionally self-contained (no cross-module imports) so the
header can be used in isolation for previews or tests.
"""

import math
import random
from typing import Dict, Optional, Tuple

import pygame

# Colors (kept local so this module is self-contained)
BLACK     = (0, 0, 0)
GREEN     = (0, 255, 0)
WHITE     = (255, 255, 255)
DIM_WHITE = (120, 120, 120)
CYAN      = (0, 200, 255)
BLUE      = (0, 160, 255)
YELLOW    = (220, 220, 0)
RED       = (255, 0, 0)

Color = Tuple[int, int, int]

# Character set for de-hash animation of the title
JAP_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&@\\/_<>[]{}()=-_")

FLASH_TIME = 0.12
FADE_TIME = 0.6

# Track per-character reveal timestamps to drive flash/fade colors
_REVEAL_TIMESTAMPS: Dict[int, float] = {}
_LAST_TITLE: str = ""
_LAST_PROGRESS: int = 0

def _animate_title_text(full_text: str, cycle_elapsed: float, scan_interval: int) -> Tuple[str, int]:
    """Return a partially revealed/dehashed version of the title text and progress.
    During the last 1 second of the cycle the title is fully revealed.

    Spaces are kept untouched so alignment remains stable while other
    characters scramble.
    """
    period = float(scan_interval)
    if period <= 1:
        return full_text, len(full_text)

    reveal = period - 1.0  # last 1s stays fully revealed
    cycle_t = cycle_elapsed % period
    if cycle_t >= reveal:
        return full_text, len(full_text)

    length = len(full_text)
    if length == 0:
        return full_text, 0

    progress = max(0, min(length, int((cycle_t / reveal) * length)))
    out_chars = []
    for i, char in enumerate(full_text):
        if char == " ":
            out_chars.append(" ")
            continue

        if i < progress:
            out_chars.append(char)
        else:
            out_chars.append(random.choice(JAP_CHARS))
    return "".join(out_chars), progress

def _lerp_color(a: Color, b: Color, t: float) -> Color:
    """Linear interpolation between two RGB colors."""
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )

def _get_countdown_color(remaining: float, scan_interval: int) -> Color:
    """Return the base color for the countdown text (no blinking logic here).
    Rules:
    - > 15s  : green (glowing handled in caller if needed)
    - 15..10 : gradient green -> yellow
    - 10..5  : gradient yellow -> red
    - 5..0   : solid red (blinking handled separately for <=3)
    """
    r = max(0.0, remaining)

    if r > 15.0:
        # Standard green
        return GREEN

    # 15 -> 10 : green -> yellow
    if 10.0 < r <= 15.0:
        t = (15.0 - r) / 5.0  # 0 at 15, 1 at 10
        return _lerp_color(GREEN, YELLOW, t)

    # 10 -> 5 : yellow -> red
    if 5.0 < r <= 10.0:
        t = (10.0 - r) / 5.0  # 0 at 10, 1 at 5
        return _lerp_color(YELLOW, RED, t)

    # 5 -> 0 : solid red
    return RED

def _reset_reveal_state_if_needed(full_text: str, progress: int) -> None:
    """Clear reveal tracking when a new cycle or title change occurs."""
    global _LAST_TITLE, _LAST_PROGRESS
    if full_text != _LAST_TITLE or progress < _LAST_PROGRESS:
        _REVEAL_TIMESTAMPS.clear()
        _LAST_TITLE = full_text
    _LAST_PROGRESS = progress

def _char_color(index: int, progress: int, base_color: Color, now: float) -> Color:
    """Determine the color for a character based on reveal timing."""
    if index >= progress:
        return base_color

    ts = _REVEAL_TIMESTAMPS.get(index)
    if ts is None:
        ts = now
        _REVEAL_TIMESTAMPS[index] = ts

    elapsed = now - ts
    if elapsed < FLASH_TIME:
        return WHITE

    fade_elapsed = elapsed - FLASH_TIME
    t = min(max(fade_elapsed / FADE_TIME, 0.0), 1.0)
    return _lerp_color(GREEN, BLUE, t)

def draw_header(
    screen: pygame.Surface,
    header_font: pygame.font.Font,
    now: float,
    cycle_start_time: float,
    scanning: bool,
    remaining: float,
    scan_interval: int,
    title_text: str,
    screen_width: int,
    version_text: Optional[str] = None,
) -> None:
    """Draw the Matrix header: animated title + version + countdown timer.

    This function does NOT clear the screen and does NOT call display.update().
    """
    if scanning:
        title_surf = header_font.render(title_text, True, BLUE)
        title_pos = (10, 8)
        screen.blit(title_surf, title_pos)

        if version_text:
            version_surf = header_font.render(version_text, True, CYAN)
            version_width = version_surf.get_width()
            title_end = title_pos[0] + title_surf.get_width()

            reserved_right = 140  # keep clear space for countdown + suffix
            preferred_x = screen_width - reserved_right - version_width - 10

            version_x = max(title_end + 10, preferred_x)
            version_y = title_pos[1]

            if version_x + version_width > screen_width - reserved_right:
                version_x = title_pos[0]
                version_y = title_pos[1] + header_font.get_height() + 2

            screen.blit(version_surf, (version_x, version_y))

        cd_text = "SCANNING..."
        cd_color = BLUE
        cd_surf = header_font.render(cd_text, True, cd_color)
        screen.blit(cd_surf, (screen_width - cd_surf.get_width() - 10, 8))
        return

    cycle_elapsed = now - cycle_start_time
    animated_title, progress = _animate_title_text(title_text, cycle_elapsed, scan_interval)

    period = float(scan_interval)
    reveal = period - 1.0
    cycle_t = cycle_elapsed % period

    if cycle_t >= reveal:
        base_title_color = BLUE
    else:
        phase = math.sin(now * 3.0)
        g_val = int(150 + 105 * (0.5 + 0.5 * phase))
        base_title_color = (0, g_val, 0)

    _reset_reveal_state_if_needed(title_text, progress)

    # Render animated title per-character to apply flash/fade coloring
    x = 10
    y = 8
    for idx, ch in enumerate(animated_title):
        color = _char_color(idx, progress, base_title_color, now)
        char_surf = header_font.render(ch, True, color)
        screen.blit(char_surf, (x, y))
        x += char_surf.get_width()

    title_width = x - 10

    # ----- Optional version tag (below the title) -----
    if version_text:
        version_surf = header_font.render(version_text, True, CYAN)
        version_x = 10
        version_y = y + header_font.get_height() + 2
        screen.blit(version_surf, (version_x, version_y))

    # ----- Countdown / SCANNING -----
    remaining_clamped = max(0.0, remaining)
    remaining_fmt = f"{remaining_clamped:.3f}"
    base_color = _get_countdown_color(remaining_clamped, scan_interval)

    if remaining_clamped <= 3.0:
        blink_on = (int(now * 4) % 2) == 0  # faster blink for urgency

        num_str = remaining_fmt
        suffix_str = "s"

        num_surf = header_font.render(num_str, True, base_color if blink_on else BLACK)
        suffix_surf = header_font.render(suffix_str, True, base_color)

        total_width = num_surf.get_width() + suffix_surf.get_width()
        x_start = screen_width - total_width - 10

        screen.blit(num_surf, (x_start, 8))
        screen.blit(suffix_surf, (x_start + num_surf.get_width(), 8))
    else:
        cd_text = f"{remaining_fmt}s"
        cd_surf = header_font.render(cd_text, True, base_color)
        screen.blit(cd_surf, (screen_width - cd_surf.get_width() - 10, 8))
