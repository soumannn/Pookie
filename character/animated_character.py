import pygame, random

class AnimatedCharacter(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Load sprite sheet
        self.sprite_sheet = pygame.image.load("assets/characters/Girl-Sheet.png").convert_alpha()
        self.frame_width = 24
        self.frame_height = 24
        self.scale_factor = 6
        self.animations = self.load_animations()

        # Default animation state
        self.current_animation = "walk_down"
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # Milliseconds per frame

        # Position and movement
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)

        # Random movement settings
        self.disable_movement = False
        self.move_timer = 0
        self.move_interval = 1000  # Change direction every 1000ms
        self.direction = random.choice(["up", "down", "left", "right"])

    def load_animations(self):
        """Load all animations from the sprite sheet."""
        frames = self.slice_frames()
        animations = {
            "walk_down": frames[16:22],  # Frames 0-3
            "walk_left": frames[4:8],  # Frames 4-7
            "walk_right": frames[8:12],  # Frames 8-11
            "walk_up": frames[12:16],  # Frames 12-15
            "idle": frames[0:4],  # Frames 16-21
            "jump_left": frames[22:28],  # Frames 22-27
            "jump_right": frames[28:34],  # Frames 28-33
            "jump_up": frames[34:40],  # Frames 34-39
            "fall_down": frames[40:44],  # Frames 40-43
            "pushup": frames[40:44],
        }
        return animations

    def slice_frames(self):
        """Extract frames from the single-row sprite sheet and scale them."""
        frames = []
        num_frames = self.sprite_sheet.get_width() // self.frame_width  # 44 frames
        for col in range(num_frames):
            frame = self.sprite_sheet.subsurface(
                pygame.Rect(col * self.frame_width, 0, self.frame_width, self.frame_height)
            )
            # Scale the frame
            scaled_frame = pygame.transform.scale(
                frame, (self.frame_width * self.scale_factor, self.frame_height * self.scale_factor)
            )
            frames.append(scaled_frame)
        return frames

    def update(self, dt):
        # Disable movement if movement is turned off (e.g., in SportModeScene)
        if not self.disable_movement:
            # Update autonomous movement direction periodically
            self.move_timer += dt
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                self.direction = random.choice(["up", "down", "left", "right"])

            # Set velocity based on direction
            if self.direction == "up":
                self.velocity.x = 0
                self.velocity.y = -1
                self.current_animation = "walk_up"
            elif self.direction == "down":
                self.velocity.x = 0
                self.velocity.y = 1
                self.current_animation = "walk_down"
            elif self.direction == "left":
                self.velocity.x = -1
                self.velocity.y = 0
                self.current_animation = "walk_left"
            elif self.direction == "right":
                self.velocity.x = 1
                self.velocity.y = 0
                self.current_animation = "walk_right"

            # Apply movement
            movement_speed = 1.5  # Slower speed
            self.rect.x += self.velocity.x * movement_speed
            self.rect.y += self.velocity.y * movement_speed

            # Restrict movement to the floor area (Y >= 346)
            if self.rect.top < 346:
                self.rect.top = 346
                self.direction = "down"

            # Keep the character within screen bounds (600x600)
            if self.rect.left < 0:
                self.rect.left = 0
                self.direction = "right"
            if self.rect.right > 600:
                self.rect.right = 600
                self.direction = "left"
            if self.rect.bottom > 600:
                self.rect.bottom = 600
                self.direction = "up"

        # Update animation frame
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.current_frame]

    def render(self, screen):
        screen.blit(self.image, self.rect)
