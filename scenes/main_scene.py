from character.animated_character import AnimatedCharacter

import pygame
from scenes.sport_mode import SportModeScene

class MainScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        # Background
        self.background = pygame.image.load("assets/backgrounds/wohnzimmer.png").convert()
        self.background = pygame.transform.scale(self.background, (600, 600))

        # Sofa
        self.sofa_image = pygame.image.load("assets/models/sofa.png").convert_alpha()
        self.sofa_image = pygame.transform.scale(self.sofa_image, (268, 170))  # Scale the sofa
        self.sofa_rect = self.sofa_image.get_rect(topleft=(107, 345))

        # Character
        self.character = AnimatedCharacter(373, 549)
        self.last_click_time = 0

    def print_click_position(self, event):
        """Print the position of a mouse click to the terminal."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at position: {event.pos}")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Print the click position
            self.print_click_position(event)

            #doppeltklick
            current_time = pygame.time.get_ticks()
            if current_time - self.last_click_time < 300:  # Detect double-click
                self.scene_manager.set_scene(SportModeScene(self.scene_manager))
            self.last_click_time = current_time

    def update(self, dt):
        self.character.update(dt)

    def render(self, screen):
        # Background render
        screen.blit(self.background, (0, 0))

        # Determine layering: character behind or in front of sofa
        character_rect = self.character.rect
        if character_rect.bottom <= self.sofa_rect.centery:  # Compare with the sofa's vertical midpoint
            # Render character first (behind sofa)
            self.character.render(screen)
            screen.blit(self.sofa_image, self.sofa_rect)
        else:
            # Render sofa first (in front of character)
            screen.blit(self.sofa_image, self.sofa_rect)
            self.character.render(screen)



