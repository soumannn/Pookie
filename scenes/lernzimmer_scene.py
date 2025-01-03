import pygame, requests
from Items import Item
from character.animated_character import AnimatedCharacter
from helper.debug_box import draw_debug_info
from config import WEATHER_URL
from datetime import datetime

class Lernzimmer:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.message_font = pygame.font.Font(None, 40)
        self.message = self.message_font.render("Learn mode!", True, (255, 255, 255))

        # Debug font
        self.debug_font = pygame.font.Font(None, 24)

        # Background
        self.bg_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        self.bg = pygame.transform.scale(self.bg_sprites[2], (600, 600))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Table
        self.table_image = pygame.image.load("assets/models/table.png").convert_alpha()
        self.table_image = pygame.transform.scale(self.table_image, (268, 170))  # Scale the sofa
        self.table_rect = self.table_image.get_rect(topleft=(240, 365))

        # Character setup
        self.character = AnimatedCharacter(426, 403)  
        self.character.disable_movement = True
        self.character.current_animation = "buch_lesen"

    def print_click_position(self, event):
        """Print the position of a mouse click to the terminal."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at position: {event.pos}")

    def update(self, dt):
        # Update the character animation
        self.character.update(dt)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln
                from scenes.wohnzimmer_scene import Wohnzimmer
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager))

    def render(self, screen, debug_mode=False):
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.message, (200, 100))
        screen.blit(self.table_image, self.table_rect)

        self.character.render(screen)

        if debug_mode: 
            # Character debug info
            draw_debug_info(
                screen,
                self.character.rect,
                f"X: {self.character.rect.x}, Y: {self.character.rect.y}",
                self.debug_font,
                text_offset=(0, self.character.rect.height + 5)  # Below the rect
            )

            # Character status
            draw_debug_info(
                screen,
                self.character.rect,
                f"{self.character.current_animation}",
                self.debug_font,
                text_offset=(0, self.character.rect.height + 25)
            )

            # Autowalk status
            draw_debug_info(
                screen,
                self.character.rect,
                f"Autowalk {'off' if self.character.disable_movement else 'on'}",
                self.debug_font,
                text_offset=(0, self.character.rect.height + 45)
            )

            # draw red box on walking ground
            pygame.draw.rect(screen, (255, 0, 0), (0, 346, 600, 600), 2)