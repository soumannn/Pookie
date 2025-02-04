import pygame, random

class AnimatedCharacter(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Walkable area boundaries (0, 270, 640, 200)
        self.walkable_left = 0
        self.walkable_top = 270 - 100
        self.walkable_right = 640
        self.walkable_bottom = 270 + 200

        # Load sprite sheet
        self.sprite_sheet = pygame.image.load("assets/characters/character.png").convert_alpha()
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

        self.dragging = False
        self.is_falling = False
        self.fall_speed = 10  # Gravity effect


        # ------ AUTONOMY SETTINGS ------- #
        self.next_action_time = pygame.time.get_ticks() + random.randint(5000, 15000)  # Next action in 5-15 seconds
        self.current_behavior = "idle"  # Start in idle state
        self.behavior_duration = 0  # Time the character will stay in the current behavior

    def schedule_next_action(self):
        """Schedule the next random action for the character."""
        self.next_action_time = pygame.time.get_ticks() + random.randint(5000, 15000)
        self.behavior_duration = random.randint(3000, 8000)  # Action lasts for 3–8 seconds

        # Randomly choose a behavior with weighted probabilities
        actions = ["walk", "read_book", "use_phone", "look_out_window", "exercise"]
        weights = [0.5, 0.15, 0.15, 0.1, 0.1]  # Adjust probabilities as needed
        self.current_behavior = random.choices(actions, weights)[0]

        # Trigger corresponding animation
        if self.current_behavior == "walk":
            self.direction = random.choice(["up", "down", "left", "right"])
        elif self.current_behavior == "read_book":
            self.force_animation("buch_lesen")
        elif self.current_behavior == "use_phone":
            self.force_animation("handy_modus")
        elif self.current_behavior == "look_out_window":
            self.force_animation("idle")  # Idle animation for looking out the window
        elif self.current_behavior == "exercise":
            self.force_animation("hantel")

    def set_position(self, x, y):
        """Set the character's position (used during dragging)."""
        print("Setting position to ({}, {})".format(x, y))
        self.current_animation = "flying"
        self.image = self.animations[self.current_animation][0]
        self.rect.x = x
        self.rect.y = y

    def start_falling(self):
        """Trigger the falling animation."""
        print("Character is falling!")
        self.is_falling = True
        self.current_animation = "fall_down"

    def setPosition(self, x, y):
        """Set the character's position (used during dragging)."""
        print("Setting position to ({}, {})".format(x, y))
        self.rect.x = x
        self.rect.y = y

    def snap_to_grid(self):
        """Snap the character back to the allowed grid."""
        if self.rect.top < 346:
            self.start_falling()  # Trigger falling animation if above grid
        else:
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > 480:
                self.rect.right = 480
            if self.rect.bottom > 480:
                self.rect.bottom = 480

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
            "flying": frames[40:44],
            "hantel": frames[44:47],
            "handy_modus": frames[47:49],
            "buch_lesen": frames[49:54]
        }
        return animations

    def slice_frames(self):
        """Extract frames from the sprite sheet and scale them."""
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

    def force_animation(self, animation_name):
        """
        Force the character to use a specific animation.
        e.g. the character should walk to the window upfront
        """
        if animation_name in self.animations:
            self.current_animation = animation_name

    def flip_bounds(self, flipped: bool):
        """
        Adjust the character's movement bounds based on the flipped state of the scene.
        When flipped, the Y-coordinates are inverted.
        """
        if flipped:
            self.allowed_top = 0
            self.allowed_bottom = 346  # The previous allowed top in normal mode
        else:
            self.allowed_top = 346
            self.allowed_bottom = 600

    def update_behavior(self, dt):
        """Update the character's behavior based on time."""
        current_time = pygame.time.get_ticks()

        # Check if it's time to perform a new action
        if current_time >= self.next_action_time:
            self.schedule_next_action()

        # Execute the current behavior
        if self.current_behavior == "walk" or self.current_behavior == "idle":
            movement_speed = 1.5

            # Randomly decide direction if no movement is set
            if self.velocity.x == 0 and self.velocity.y == 0:
                self.direction = random.choice(["up", "down", "left", "right"])

            if self.direction == "up":
                self.velocity.x = 0
                self.velocity.y = -1
                self.force_animation("walk_up")
            elif self.direction == "down":
                self.velocity.x = 0
                self.velocity.y = 1
                self.force_animation("walk_down")
            elif self.direction == "left":
                self.velocity.x = -1
                self.velocity.y = 0
                self.force_animation("walk_left")
            elif self.direction == "right":
                self.velocity.x = 1
                self.velocity.y = 0
                self.force_animation("walk_right")

            # Apply movement
            self.rect.x += self.velocity.x * movement_speed
            self.rect.y += self.velocity.y * movement_speed

            # Constrain feet (bottom of the rectangle) to walkable area
            if self.rect.bottom > self.walkable_bottom:
                self.rect.bottom = self.walkable_bottom
                self.direction = "up"
            if self.rect.bottom - self.frame_height * self.scale_factor < self.walkable_top:
                self.rect.bottom = self.walkable_top + self.frame_height * self.scale_factor
                self.direction = "down"
            if self.rect.left < self.walkable_left:
                self.rect.left = self.walkable_left
                self.direction = "right"
            if self.rect.right > self.walkable_right:
                self.rect.right = self.walkable_right
                self.direction = "left"

        elif self.current_behavior in ["read_book", "use_phone", "look_out_window", "exercise"]:
            # Stay in the current animation for the behavior's duration
            if current_time >= self.next_action_time - self.behavior_duration:
                self.current_behavior = "walk"  # Revert to walking after the behavior ends

    def update(self, dt):
        if self.is_falling:
            # Apply gravity effect
            self.rect.y += self.fall_speed

            # Check if the character is close enough to the grid
            if abs(self.rect.top - 346) <= self.fall_speed:
                print("Character landed.")
                self.rect.top = 346  # Snap to the grid
                self.is_falling = False  # Stop falling
                self.current_animation = "idle"  # Reset to idle animation

        elif not self.disable_movement:
            self.update_behavior(dt)

        # Update animation frame
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.current_frame]

    def render(self, screen):
        screen.blit(self.image, self.rect)

