import pygame
from Items import Item
from character.animated_character import AnimatedCharacter
from helper.debug_box import draw_debug_info


class Esszimmer:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        self.original_width, self.original_height = 736, 598  # Originalgröße des Bildes
        self.bg_image = pygame.image.load("assets/backgrounds/kitchen.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg_image, (600, 600))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        self.character = AnimatedCharacter(0, 346)  # Start at left edge
        self.character.disable_movement = True
        self.character.current_animation = "walk_right"  # Walk animation


    def update(self, dt):
        self.character.update(dt)

    def render(self, screen, debug_mode=False):
        # Rendern der Esszimmer-Szene
        screen.blit(self.bg, self.bg_rect)
        self.character.render(screen)


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln
                from scenes.wohnzimmer_scene import Wohnzimmer
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager))

