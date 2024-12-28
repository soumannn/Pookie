from Items import Item
import pygame

class DachbodenScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        self.index = 0

        # Hintergrund
        self.background_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        self.background = pygame.transform.scale(self.background_sprites[self.index],(600,600))


        # Pookie

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.index += 1
            self.background = pygame.transform.scale(self.background_sprites[self.index],(600,600))

    def update(self, dt):
        pass

    def render(self, screen):
        screen.blit(self.background, (0,0))

