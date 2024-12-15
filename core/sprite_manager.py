import pygame

class MovingSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = pygame.math.Vector2(2, 0)

    def update(self):
        self.rect.x += self.velocity.x
