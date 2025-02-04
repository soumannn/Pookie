import sys

import pygame
from core.scene_manager import SceneManager
from scenes.wohnzimmer_scene import Wohnzimmer
from core.pookie import Pookie

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))  # Start in windowed mode
    pygame.display.set_caption("Pookie")
    clock = pygame.time.Clock()

    #locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')  # For Linux/Mac
    # locale.setlocale(locale.LC_TIME, 'German_Germany.1252')

    scene_manager = SceneManager()
    scene_manager.set_scene(Wohnzimmer(scene_manager, Pookie(scene_manager)))

    debug_mode = False  # Debug mode toggle
    fullscreen = False  # Fullscreen toggle state

    running = True
    while running:
        dt = clock.tick(60)  # 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Toggle debug mode with 'D' key
                if event.key == pygame.K_d:
                    debug_mode = not debug_mode
                # Toggle fullscreen with 'F' key
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((480, 320))
            scene_manager.handle_event(event)

        scene_manager.update(dt)
        scene_manager.render(screen, debug_mode)  # Pass debug mode
        pygame.display.flip()


    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()
