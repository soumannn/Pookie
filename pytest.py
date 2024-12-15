import pygame
import sys
import os

# Ensure compatibility on macOS
os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"  # Optional: Set window position

# Initialize Pygame
pygame.init()

# Screen setup
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Sprite Scaling Example")

# Colors
background_color = (50, 150, 200)  # Light blue

# Sprite class
class CatSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, frame_width, frame_height, scale_factor=2):
        super().__init__()
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale_factor = scale_factor

        # Load and scale frames
        self.frames = self._load_frames()
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))

        # Animations
        self.animation_timer = 0
        self.animation_speed = 150  # ms per frame

    def _load_frames(self):
        frames = []
        sheet_width = self.sprite_sheet.get_width()

        # Extract and scale each frame
        for x in range(0, sheet_width, self.frame_width):
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, 0, self.frame_width, self.frame_height))
            scaled_frame = pygame.transform.scale(
                frame,
                (self.frame_width * self.scale_factor, self.frame_height * self.scale_factor)
            )
            frames.append(scaled_frame)
        return frames

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

# Load the sprite sheet
try:
    sprite_sheet = pygame.image.load("assets/models/Idle.png").convert_alpha()
except pygame.error as e:
    print(f"Error loading sprite sheet: {e}")
    sys.exit()

# Sprite setup
frame_width = 32
frame_height = 32
scale_factor = 4  # Scale the sprite 4x its original size
cat_sprite = CatSprite(sprite_sheet, frame_width, frame_height, scale_factor)
all_sprites = pygame.sprite.Group(cat_sprite)

# Main loop
clock = pygame.time.Clock()
running = True

try:
    while running:
        dt = clock.tick(60)  # Limit to 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill(background_color)

        # Update and draw sprites
        all_sprites.update(dt)
        all_sprites.draw(screen)

        # Update display
        pygame.display.flip()
except Exception as e:
    print(f"Error during runtime: {e}")
finally:
    pygame.quit()
    sys.exit()
