import pygame
from core.scene_manager import SceneManager
from scenes.main_scene import MainScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Pookie")
    clock = pygame.time.Clock()

    scene_manager = SceneManager()
    scene_manager.set_scene(MainScene(scene_manager))

    running = True
    while running:
        dt = clock.tick(60)  # 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)

        scene_manager.update(dt)
        scene_manager.render(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
