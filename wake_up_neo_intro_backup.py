# Backup of wake_up_neo_intro.py

import pygame
import random
import time
import sys

pygame.init()
pygame.font.init()

# FULLSCREEN 480x320 for Pi display
WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

# Colors
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (80, 150, 255)

# Fonts
font = pygame.font.SysFont("dejavusansmono", 14)           # intro
loader_font = pygame.font.SysFont("dejavusansmono", 12)    # loader

# Intro line position (top-left)
LINE_X = 10
LINE_Y = 10

# Loader layout
LOADER_START_Y = 60
LOADER_LINE_SPACING = 18

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

# ---------- INTRO (single line, white square cursor) ----------

def render_intro_line(text, visible_chars, show_cursor=True):
    screen.fill(BLACK)
    visible_text = text[:visible_chars]
    text_surf = font.render(visible_text, True, GREEN)
    screen.blit(text_surf, (LINE_X, LINE_Y))

    if show_cursor:
        cursor_x = LINE_X + text_surf.get_width() + 4
        cursor_y = LINE_Y + 2
        cursor_size = font.get_height() - 4
        pygame.draw.rect(screen, WHITE, (cursor_x, cursor_y, cursor_size, cursor_size))

    pygame.display.update()

def type_sentence(sentence, min_delay=70, max_delay=140):
    """Slow, human-like typing for intro line."""
    for i in range(len(sentence) + 1):
        handle_events()
        render_intro_line(sentence, i, show_cursor=True)
        pygame.time.delay(random.randint(min_delay, max_delay))

def delete_sentence(sentence, min_delay=40, max_delay=80):
    """Delete characters one by one (backspace effect)."""
    for i in range(len(sentence), -1, -1):
        handle_events()
        render_intro_line(sentence, i, show_cursor=True)
        pygame.time.delay(random.randint(min_delay, max_delay))

# ---------- LOADER (shell-style: commands typed, responses instant) ----------

def render_loader_screen(history_lines, current_text, current_color, show_cursor=True):
    """
    Draw all previous loader lines (with their own colors)
    + current line being typed (with white square cursor).
    history_lines: list of (text, color)
    """
    screen.fill(BLACK)

    y = LOADER_START_Y
    for line_text, line_color in history_lines:
        line_surf = loader_font.render(line_text, True, line_color)
        screen.blit(line_surf, (10, y))
        y += LOADER_LINE_SPACING

    current_y = LOADER_START_Y + len(history_lines) * LOADER_LINE_SPACING
    visible_surf = loader_font.render(current_text, True, current_color)
    screen.blit(visible_surf, (10, current_y))

    if show_cursor:
        cursor_x = 10 + visible_surf.get_width() + 3
        cursor_y = current_y + 1
        cursor_size = loader_font.get_height() - 3
        pygame.draw.rect(screen, WHITE, (cursor_x, cursor_y, cursor_size, cursor_size))

    pygame.display.update()

def type_command_line(cmd_text, history_lines, min_delay=25, max_delay=55):
    """
    Simulate hacker typing a command line.
    Command shown in green, with typing effect.
    """
    current = ""
    for i in range(len(cmd_text) + 1):
        handle_events()
        current = cmd_text[:i]
        render_loader_screen(history_lines, current, GREEN, show_cursor=True)
        pygame.time.delay(random.randint(min_delay, max_delay))

    history_lines.append((cmd_text, GREEN))
    pygame.time.delay(120)

def instant_system_response(resp_text, history_lines):
    """
    System response appears immediately as full line in blue (no typing).
    """
    render_loader_screen(history_lines, resp_text, BLUE, show_cursor=False)
    pygame.time.delay(150)
    history_lines.append((resp_text, BLUE))

def securing_link(history_lines):
    base = "Securing link against Agents"
    dots = 0
    start = time.time()

    while time.time() - start < 4:
        handle_events()
        text = base + "." * dots

        screen.fill(BLACK)
        y = LOADER_START_Y
        for line_text, line_color in history_lines:
            line_surf = loader_font.render(line_text, True, line_color)
            screen.blit(line_surf, (10, y))
            y += LOADER_LINE_SPACING

        current_y = LOADER_START_Y + len(history_lines) * LOADER_LINE_SPACING
        current_surf = loader_font.render(text, True, BLUE)
        screen.blit(current_surf, (10, current_y))

        cursor_x = 10 + current_surf.get_width() + 3
        cursor_y = current_y + 1
        cursor_size = loader_font.get_height() - 3
        pygame.draw.rect(screen, WHITE, (cursor_x, cursor_y, cursor_size, cursor_size))

        pygame.display.update()
        pygame.time.delay(250)
        dots = (dots + 1) % 9

# ---------- SEQUENCES ----------

def run_intro():
    sentences = [
        "Wake up, Neo",
        "The Matrix has you...",
        "Follow the white rabbit.",
        "Knock, knock, Neo."
    ]

    for s in sentences[:-1]:
        type_sentence(s)
        pygame.time.delay(700)
        delete_sentence(s)

    final = sentences[-1]
    type_sentence(final)
    pygame.time.delay(1000)

    for _ in range(4):
        handle_events()
        render_intro_line(final, len(final), show_cursor=True)
        pygame.time.delay(200)
        render_intro_line(final, len(final), show_cursor=False)
        pygame.time.delay(200)

def run_loader():
    script = [
        (
            "zion@nebuchadnezzar:~# Boot Nebuchadnezzar.os",
            "nebuchadnezzar: core systems online"
        ),
        (
            "zion@nebuchadnezzar:~# scan_matrix --trace-signal neo",
            "matrix: carrier signal locked | host: NEO | status: AWAKE"
        ),
        (
            "zion@nebuchadnezzar:~# open_tunnel --zion-mainframe --stealth",
            "tunnel: encrypted backdoor opened | route: zion/core/matrix"
        ),
        (
            "zion@nebuchadnezzar:~# establish_link --agent-free",
            "link: secure channel established | agents: NOT PRESENT"
        ),
    ]

    history = []

    for cmd, resp in script:
        type_command_line(cmd, history)
        instant_system_response(resp, history)

    securing_link(history)

def main():
    run_intro()
    run_loader()
    pygame.time.delay(600)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
