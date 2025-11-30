
"""Animated Matrix-style header for the Wi-Fi console.

This module handles the title "dehashing" animation, blinking cursor, and the
color-shifting countdown indicator displayed at the top of the console. It is
intentionally self-contained (no cross-module imports) so the header can be
used in isolation for previews or tests.
"""

import math
import random
import time
from typing import Optional, Tuple

import pygame

# Colors (kept local so this module is self-contained)
BLACK     = (0, 0, 0)
GREEN     = (0, 255, 0)
WHITE     = (255, 255, 255)
DIM_WHITE = (120, 120, 120)
BLUE      = (0, 160, 255)
YELLOW    = (220, 220, 0)
RED       = (255, 0, 0)

Color = Tuple[int, int, int]

CURSOR_CHAR = "▌"

# Character set for de-hash animation of the title
JAP_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&@\\/_<>[]{}()=-_")

def _animate_title_text(full_text: str, cycle_elapsed: float, scan_interval: int) -> str:
    """Return a partially revealed/dehashed version of the title text.
    During the last 1 second of the cycle the title is fully revealed.

    Spaces are kept untouched so alignment remains stable while other
    characters scramble.
    """
    period = float(scan_interval)
    if period <= 1:
        return full_text

    reveal = period - 1.0  # last 1s stays fully revealed
    cycle_t = cycle_elapsed % period
    if cycle_t >= reveal:
        return full_text

    length = len(full_text)
    if length == 0:
        return full_text

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
    return "".join(out_chars)

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
    # ----- Title with de-hash animation -----
    cursor_visible = (int(now * 2) % 2) == 0  # ~2 Hz blink

    if scanning:
        # During scanning we always show the full title in blue
        base_title = title_text
        title_color = BLUE
    else:
        cycle_elapsed = now - cycle_start_time
        base_title = _animate_title_text(title_text, cycle_elapsed, scan_interval)

        # Glow effect for green phase; switches to blue in the last second
        period = float(scan_interval)
        reveal = period - 1.0
        cycle_t = cycle_elapsed % period

        if cycle_t >= reveal:
            title_color = BLUE
        else:
            phase = math.sin(now * 3.0)
            g_val = int(150 + 105 * (0.5 + 0.5 * phase))
            title_color = (0, g_val, 0)

    if cursor_visible:
        display_title = base_title + CURSOR_CHAR
    else:
        display_title = base_title + " "

    title_surf = header_font.render(display_title, True, title_color)
    title_pos = (10, 8)
    screen.blit(title_surf, title_pos)

    # ----- Optional version tag -----
    if version_text:
        version_surf = header_font.render(version_text, True, DIM_WHITE)
        version_x = title_pos[0] + title_surf.get_width() + 10

        # keep clear space for countdown on the right
        max_x = screen_width - version_surf.get_width() - 80
        version_x = min(version_x, max_x)

        screen.blit(version_surf, (version_x, title_pos[1]))

    # ----- Countdown / SCANNING -----
    if scanning:
        cd_text = "SCANNING..."
        cd_color = BLUE
        cd_surf = header_font.render(cd_text, True, cd_color)
        screen.blit(cd_surf, (screen_width - cd_surf.get_width() - 10, 8))
        return

    # Normal countdown: XXs
    remaining_clamped = max(0.0, remaining)
    remaining_int = int(remaining_clamped)
    base_color = _get_countdown_color(remaining_clamped, scan_interval)

    # Last 3 seconds: blink only the numeric part
    if remaining_clamped <= 3.0:
        blink_on = (int(now * 4) % 2) == 0  # faster blink for urgency

        num_str = f"{remaining_int}"
        suffix_str = "s"

        num_surf = header_font.render(num_str, True, base_color if blink_on else BLACK)
        suffix_surf = header_font.render(suffix_str, True, base_color)

        total_width = num_surf.get_width() + suffix_surf.get_width()
        x_start = screen_width - total_width - 10

        screen.blit(num_surf, (x_start, 8))
        screen.blit(suffix_surf, (x_start + num_surf.get_width(), 8))
    else:
        # Normal colored countdown (no blinking)
        cd_text = f"{remaining_int}s"
        cd_surf = header_font.render(cd_text, True, base_color)
        screen.blit(cd_surf, (screen_width - cd_surf.get_width() - 10, 8))
