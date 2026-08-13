"""Cat Invasion — entry point.

Defend the skies from the invading cats. A polished free-roam arena shooter
built with pygame. Run with:  python Main.py
"""

import sys

import pygame


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        pygame.mixer.init(44100, -16, 2, 512)
    except pygame.error as exc:
        print(f"[main] audio unavailable, continuing muted: {exc}")

    import assets
    assets.load_all_sounds()
    assets.play_music(0.35)

    from game import Game
    Game().run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
