import pygame
import random
import time
import sys

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Japanese Matrix rain font (slightly larger)
try:
    matrix_font = pygame.font.SysFont("IPAGothic", 12)
except:
    matrix_font = pygame.font.SysFont("NotoSansCJK-Regular", 12)

USE_ASCII_ONLY_FOR_RAIN = False

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

def apply_global_fade(fade_amount):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(int(fade_amount * 255))
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

def matrix_rain():
    matrix_chars = (
        [chr(code) for code in range(0x30A0, 0x30FF)]
        if not USE_ASCII_ONLY_FOR_RAIN
        else list("01<>\\/=-+*{}[]!@#$%^&*ABCDEFGHJKLMNPQRSTUVWXYZ")
    )

    _, char_height = matrix_font.size("ア")

    num_streams = 21
    spacing = WIDTH / num_streams

    drops = [random.uniform(-25, -5) for _ in range(num_streams)]
    active = [True] * num_streams
    speeds = [random.uniform(0.7, 1.15) for _ in range(num_streams)]
    drifts = [random.uniform(-0.15, 0.15) for _ in range(num_streams)]

    fade_time = 2.0
    start_time = time.time()

    while True:
        handle_events()
        t = time.time() - start_time

        trail = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        trail.fill((0, 0, 0, 90))
        screen.blit(trail, (0, 0))

        all_finished = True

        for i in range(num_streams):
            if not active[i]:
                continue

            all_finished = False
            x = int(i * spacing)
            head_pos = drops[i] * char_height

            max_trail_segments = 14
            for seg in range(max_trail_segments):
                y = head_pos - seg * char_height

                if 0 <= y < HEIGHT:
                    char = random.choice(matrix_chars)
                    base_fade = max(0.0, 1.0 - seg * 0.07)
                    faded = base_fade * 0.40
                    g = int(255 * faded)
                    color = (0, g, 0)
                    surf = matrix_font.render(char, True, color)
                    screen.blit(surf, (x, int(y)))

            if 0 <= head_pos < HEIGHT + char_height:
                char = random.choice(matrix_chars)
                head_surf = matrix_font.render(char, True, (200, 200, 200))
                screen.blit(head_surf, (x, int(head_pos)))

            drops[i] += speeds[i]
            if random.random() < 0.2:
                drops[i] += drifts[i] * 0.1

            if drops[i] * char_height > HEIGHT + char_height:
                active[i] = False

        if all_finished:
            pygame.display.update()
            break

        if t < fade_time:
            fade_amount = 1.0 - (t / fade_time)
            apply_global_fade(fade_amount)

        pygame.display.update()
        pygame.time.delay(55)

def main():
    screen.fill(BLACK)
    pygame.display.set_caption("Matrix Rain")
    matrix_rain()
    screen.fill(BLACK)
    pygame.display.update()
    pygame.time.delay(400)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
