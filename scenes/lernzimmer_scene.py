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
        self.table_image = pygame.transform.scale(self.table_image, (268, 170))
        self.table_rect = self.table_image.get_rect(topleft=(330, 430))

        # Chair
        self.chair_image = pygame.image.load("assets/models/chair.png").convert_alpha()
        self.chair_image = pygame.transform.scale(self.chair_image, (100, 140))
        self.chair_rect = self.chair_image.get_rect(topleft=(415, 330))

        # Carpet 
        self.carpet_image = pygame.image.load("assets/models/carpet.png").convert_alpha()
        self.carpet_image = pygame.transform.scale(self.carpet_image, (312, 208))
        self.carpet_rect = self.carpet_image.get_rect(topleft=(288, 392))

        # Big Bookshelf 
        self.bookshelf_b_image = pygame.image.load("assets/models/bookshelf_big.png").convert_alpha()
        self.bookshelf_b_image = pygame.transform.scale(self.bookshelf_b_image, (276, 282))
        self.bookshelf_b_rect = self.bookshelf_b_image.get_rect(topleft=(5, 120))

        # Tablelamp
        self.table_lamp_sprites = Item("assets/spritesheets/tablelamps.png", 15, 23, 1, 2)
        self.table_lamp = pygame.transform.scale(self.table_lamp_sprites[1], (60, 92))
        self.table_lamp_rect = self.table_lamp.get_rect(topleft=(530, 430))

        # Character setup
        self.character = AnimatedCharacter(0, 346)  
        self.character.disable_movement = True
        self.character.current_animation = "walk_right"
        self.is_walking = True  # Start walking to chair

    def print_click_position(self, event):
        """Print the position of a mouse click to the terminal."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at position: {event.pos}")

    def handle_walk_to_chair(self):
        target_x = self.chair_rect.centerx - 10
        target_y = self.chair_rect.centery - 35
        character_center = self.character.rect.center

        # Calculate direction
        direction_x = target_x - character_center[0]
        direction_y = target_y - character_center[1]

        # Normalize direction
        distance = max(abs(direction_x), abs(direction_y))
        if distance > 0:
            self.character.velocity.x = direction_x / distance
            self.character.velocity.y = direction_y / distance

        # Move character
        movement_speed = 2  # Speed for walking to the target
        self.character.rect.x += self.character.velocity.x * movement_speed
        self.character.rect.y += self.character.velocity.y * movement_speed

        # Check if the character reached the target position
        if abs(character_center[0] - target_x) < 5 and abs(character_center[1] - target_y) < 5:
            self.is_walking = False  # Stop walking
            self.character.current_animation = "buch_lesen"

    def handle_left_learn_room(self):
        pass
    
    def update(self, dt):
        if self.is_walking:
            self.handle_walk_to_chair()

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
        screen.blit(self.bookshelf_b_image, self.bookshelf_b_rect)
        screen.blit(self.carpet_image, self.carpet_rect)
        screen.blit(self.chair_image, self.chair_rect)
        screen.blit(self.table_image, self.table_rect)
        screen.blit(self.table_lamp, self.table_lamp_rect)
        
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

            # Table Lamp debug info
            draw_debug_info(
                screen,
                self.table_lamp_rect,
                f"X: {self.table_lamp_rect.x}, Y: {self.table_lamp_rect.y}",
                self.debug_font
            )

            # Table debug info
            draw_debug_info(
                screen,
                self.table_rect,
                f"X: {self.table_rect.x}, Y: {self.table_rect.y}",
                self.debug_font
            )

            # Chair debug info
            draw_debug_info(
                screen,
                self.chair_rect,
                f"X: {self.chair_rect.x}, Y: {self.chair_rect.y}",
                self.debug_font
            )

            # Carpet debug info
            draw_debug_info(
                screen,
                self.carpet_rect,
                f"X: {self.carpet_rect.x}, Y: {self.carpet_rect.y}",
                self.debug_font
            )

            # Big Bookshelf debug info
            draw_debug_info(
                screen,
                self.bookshelf_b_rect,
                f"X: {self.bookshelf_b_rect.x}, Y: {self.bookshelf_b_rect.y}",
                self.debug_font
            )