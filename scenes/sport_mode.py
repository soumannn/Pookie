import pygame
from Items import Item
from character.animated_character import AnimatedCharacter


class SportModeScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.message_font = pygame.font.Font(None, 40)
        self.message = self.message_font.render("Sport Mode!", True, (255, 255, 255))

        #city

        # Load the city skyline images 50 100 150 200
        self.city_layers = [
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/2.png").convert_alpha(), "y": -40, "speed": 0.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/3.png").convert_alpha(), "y": -20, "speed": 1.0, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/4.png").convert_alpha(), "y": 20, "speed": 1.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/5.png").convert_alpha(), "y": 20, "speed": 2.0, "x": 0}
        ]


        #bg
        self.bg_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        # Scale the first sprite from the list
        self.bg = pygame.transform.scale(self.bg_sprites[4], (600, 600))
        # Create a rect for positioning
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        #char
        # Character setup
        self.character = AnimatedCharacter(0, 346)  # Start at the left edge
        self.character.disable_movement = True
        self.character.current_animation = "walk_right"  # Walk animation

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Return to the main scene
                from scenes.main_scene import MainScene
                self.scene_manager.set_scene(MainScene(self.scene_manager))

    def update(self, dt):

        # Move the character to the right
        movement_speed = 2  # Character walking speed
        self.character.rect.x += movement_speed

        # Loop character position if they reach the screen edge
        if self.character.rect.x > 600:
            self.character.rect.x = -self.character.rect.width

        # Scroll each city layer
        for layer in self.city_layers:
            layer["x"] -= layer["speed"]
            if layer["x"] <= -600:  # Reset position for seamless scrolling
                layer["x"] = 0

        # Update the character animation
        self.character.update(dt)

    def render(self, screen):
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.message, (200, 100))

        for layer in self.city_layers:
            screen.blit(layer["image"], (layer["x"], layer["y"]))  # First part
            screen.blit(layer["image"], (layer["x"] + 600, layer["y"]))

        self.character.render(screen)
