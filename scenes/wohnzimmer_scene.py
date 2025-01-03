from character.animated_character import AnimatedCharacter
from Items import Item
from helper.debug_box import draw_debug_info

import pygame
from scenes.joggen_scene import JoggenScene
from scenes.lernzimmer_scene import Lernzimmer
import requests
from datetime import datetime
from config import WEATHER_URL


class Wohnzimmer:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        # debug-font
        self.debug_font = pygame.font.Font(None, 24)

        self.falling = False
        self.fall_speed = 5  # Geschwindigkeit des Fallens
        self.scene_flipped = False  # Tracks whether the scene is flipped

        self.walk_to = False  # New state for TikTok mode
        self.walk_to_target = None
        self.walk_to_animation = ""

        self.movement_resume_timer = 0
        self.resume_movement_delay = 500  # 500ms delay before resuming random movement

        # Zielpositionen für fallende Objekte
        self.character_target_y = 600
        self.window_target_y = 600
        self.door_target_y = 600
        self.sofa_target_y = 600
        self.lamp_target_y = 600

        # Time and weather setup
        self.message_font = pygame.font.SysFont('system-ui', 40)
        self.message_font_uhrzeit = pygame.font.SysFont('system-ui', 40)
        self.weather_info = "Loading weather..."
        self.last_weather_update = pygame.time.get_ticks()
        self.update_weather()

        # Clock setup
        self.clock = pygame.time.Clock()

        self.bg_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        # Scale the first sprite from the list
        self.bg = pygame.transform.scale(self.bg_sprites[2], (600, 600))
        # Create a rect for positioning
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Windows
        self.current_weather_index = 0
        self.window_sprites = Item("assets/spritesheets/windows.png", 32, 28, 1, 4)
        self.window = pygame.transform.scale(self.window_sprites[self.current_weather_index], (128, 128))
        self.window_rect = self.window.get_rect(topleft=(393, 120))
        self.walk_to_window = False

        # Sofa
        self.sofa_image = pygame.image.load("assets/models/sofa.png").convert_alpha()
        self.sofa_image = pygame.transform.scale(self.sofa_image, (268, 170))  # Scale the sofa
        self.sofa_rect = self.sofa_image.get_rect(topleft=(240, 365))

        # Character
        self.character = AnimatedCharacter(373, 549)
        self.last_click_time = 0
        self.dragging_character = False

        # State for transitioning to sport mode (Walk to Door)
        self.door_index = 0
        self.transition_to_sport_mode = False
        self.door_open_timer = 0
        self.walk_to_door = False

        # State for transitioning to learn mode (Walk to Learnroom)
        self.transition_to_learn_mode = False
        self.walk_to_learnroom = False

        # Door
        self.door_sprites = Item("assets/spritesheets/doors.png", 30, 51, 1, 3)
        self.door = pygame.transform.scale(self.door_sprites[self.door_index], (130, 200))
        self.door_rect = self.window.get_rect(topleft=(40, 160))

        # Standinglamp
        self.stand_lamp_sprites = Item("assets/spritesheets/standinglamps.png", 15, 46, 1, 2)
        self.standing_lamp = pygame.transform.scale(self.stand_lamp_sprites[self.current_weather_index], (70, 199))
        self.standing_lamp_rect = self.standing_lamp.get_rect(topleft=(510, 376))

        self.update_weather()
        self.set_day_night()

    def print_click_position(self, event):
        """Print the position of a mouse click to the terminal."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at position: {event.pos}")

    def update_weather(self):
        """Fetch the weather data from OpenWeatherMap."""
        try:
            response = requests.get(WEATHER_URL)
            data = response.json()
            if data.get("cod") == 200:
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                self.weather_info = f"{weather}, {temp:.1f}°C"

                # Set day or night using sunrise and sunset
                self.sunrise = data["sys"]["sunrise"]
                self.sunset = data["sys"]["sunset"]
            else:
                self.weather_info = "Fehler beim Laden der Wetterdaten."
        except Exception as e:
            self.weather_info = "Keine Wetterdaten verfügbar."

    def set_day_night(self):
        """Set day or night based on sunrise and sunset times."""
        try:
            current_time = datetime.now().timestamp()
            if self.sunrise <= current_time < self.sunset:
                self.current_weather_index = 0  # Day
            else:
                self.current_weather_index = 1  # Night

            self.window = pygame.transform.scale(self.window_sprites[self.current_weather_index], (128, 128))
            self.standing_lamp = pygame.transform.scale(self.stand_lamp_sprites[self.current_weather_index], (70, 199))

        except AttributeError:
            # Default to day if sunrise/sunset not available
            self.current_weather_index = 0

    def handle_walk_to(self):
        """Handle walking to the TikTok target position."""
        target_x, target_y = self.walk_to_target
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
            self.walk_to = False  # Stop walking
            self.character.force_animation(self.walk_to_animation)  # Switch to handy_modus

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Print the click position
            self.print_click_position(event)

            # Detect clicks on the window
            if self.window_rect.collidepoint(event.pos):  # Check if click is within window rectangle
                # Toggle indices
                if self.current_weather_index == 0:
                    self.current_weather_index = 2
                elif self.current_weather_index == 2:
                    self.current_weather_index = 0
                elif self.current_weather_index == 1:
                    self.current_weather_index = 3
                elif self.current_weather_index == 3:
                    self.current_weather_index = 1

                # Update the window sprite
                self.window = pygame.transform.scale(self.window_sprites[self.current_weather_index], (128, 128))

            # Detect character drag
            if self.character.rect.collidepoint(event.pos):  # Start dragging
                print("picking up....")
                self.character.disable_movement = True
                self.dragging_character = True
                self.character.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_character:  # Stop dragging
                print("let go")
                self.character.disable_movement = False
                self.dragging_character = False
                self.character.dragging = False
                self.character.snap_to_grid()  # Snap back to the allowed grid

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_character:  # Update position while dragging
                print("dragging..")
                self.character.set_position(event.pos[0] - self.character.rect.width // 2,
                                            event.pos[1] - self.character.rect.height // 2)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                # Use an index to toggle
                self.current_weather_index = 1 - self.current_weather_index  # Toggles between 0 and 1
                self.window = pygame.transform.scale(self.window_sprites[self.current_weather_index], (128, 128))
                self.standing_lamp = pygame.transform.scale(self.stand_lamp_sprites[self.current_weather_index],
                                                            (70, 199))
            elif event.key == pygame.K_s:
                self.walk_to_door = True  # Start walking to the door

            elif event.key == pygame.K_o:
                self.walk_to_window = True

            elif event.key == pygame.K_h:
                self.character.disable_movement = True
                self.character.force_animation("hantel")

            elif event.key == pygame.K_t:
                """TikTok Modus
                Walk to (426, 453) and switch to 'handy_modus'."""
                self.character.disable_movement = True
                self.walk_to_animation = "handy_modus"
                self.walk_to = True
                self.walk_to_target = (426, 403)  # Target position for TikTok mode

            elif event.key == pygame.K_b:
                """Buch lesen Modus"""
                #self.character.disable_movement = True
                #self.walk_to_animation = "buch_lesen"
                #self.walk_to = True
                #self.walk_to_target = (426, 403)
                #self.walking_to_learnroom = True    # Start walking to learn room
                self.scene_manager.set_scene(Lernzimmer(self.scene_manager))
                
            elif event.key == pygame.K_DOWN:  # Pfeil nach unten
                self.falling = True
                self.flip_scene()

            elif event.key == pygame.K_r:  # Zurücksetzen
                    print("restart")
                    self.falling = False
                    self.reset_positions()

    def reset_positions(self):
        self.character.rect.y = 549
        self.window_rect.y = 120
        self.door_rect.y = 160
        self.sofa_rect.y = 365
        self.standing_lamp_rect.y = 376

    def flip_scene(self):
        """Flip the entire scene upside down, including bounds."""
        self.scene_flipped = not self.scene_flipped
        self.character.flip_bounds(self.scene_flipped)

    def everything_falls(self):
        """Make all objects in the scene fall (including character)."""
        # Character falls
        if self.scene_flipped:
            if self.character.rect.top > 0:
                self.character.rect.y -= self.fall_speed
            else:
                self.character.rect.y = 0
        else:
            if self.character.rect.bottom < 600:
                self.character.rect.y += self.fall_speed
            else:
                self.character.rect.y = 600 - self.character.rect.height

        # Window falls
        if self.scene_flipped:
            if self.window_rect.top > 0:
                self.window_rect.y -= self.fall_speed
            else:
                self.window_rect.y = 0
        else:
            if self.window_rect.bottom < 600:
                self.window_rect.y += self.fall_speed
            else:
                self.window_rect.y = 600 - self.window_rect.height

        # Door falls
        if self.scene_flipped:
            if self.door_rect.top > 0:
                self.door_rect.y -= self.fall_speed
            else:
                self.door_rect.y = 0
        else:
            if self.door_rect.bottom < 600:
                self.door_rect.y += self.fall_speed
            else:
                self.door_rect.y = 600 - self.door_rect.height

        # Sofa falls
        if self.scene_flipped:
            if self.sofa_rect.top > 0:
                self.sofa_rect.y -= self.fall_speed
            else:
                self.sofa_rect.y = 0
        else:
            if self.sofa_rect.bottom < 600:
                self.sofa_rect.y += self.fall_speed
            else:
                self.sofa_rect.y = 600 - self.sofa_rect.height

        # Lamp falls
        if self.scene_flipped:
            if self.standing_lamp_rect.top > 0:
                self.standing_lamp_rect.y -= self.fall_speed
            else:
                self.standing_lamp_rect.y = 0
        else:
            if self.standing_lamp_rect.bottom < 600:
                self.standing_lamp_rect.y += self.fall_speed
            else:
                self.standing_lamp_rect.y = 600 - self.standing_lamp_rect.height

    def handle_walk_to_window(self):
        if self.walk_to_window:
            self.character.disable_movement = True
            self.character.force_animation("walk_up")
            window_center = self.window_rect.center
            character_center = self.character.rect.center

            direction_x = window_center[0] - character_center[0]
            direction_y = window_center[1] - character_center[1]

            # Normalize direction
            distance = max(abs(direction_x), abs(direction_y))
            if distance > 0:
                self.character.velocity.x = direction_x / distance
                self.character.velocity.y = direction_y / distance

            # Move character
            movement_speed = 2  # Faster speed for walking to the door
            self.character.rect.x += self.character.velocity.x * movement_speed
            self.character.rect.y += self.character.velocity.y * movement_speed

            if self.character.rect.colliderect(self.window_rect):
                self.walk_to_window = False

                # Switch weather
                if self.current_weather_index == 0:
                    self.current_weather_index = 2
                elif self.current_weather_index == 2:
                    self.current_weather_index = 0
                elif self.current_weather_index == 1:
                    self.current_weather_index = 3
                elif self.current_weather_index == 3:
                    self.current_weather_index = 1

                # Update the window sprite
                self.window = pygame.transform.scale(self.window_sprites[self.current_weather_index], (128, 128))

                # Start movement resume timer
                self.movement_resume_timer = self.resume_movement_delay

    def handle_walk_to_door(self):
        self.character.disable_movement = True
        self.character.force_animation("walk_left")
        # Move character toward the door
        door_center = self.door_rect.center
        character_center = self.character.rect.center

        # Calculate direction
        direction_x = door_center[0] - character_center[0]
        direction_y = door_center[1] - character_center[1]

        # Normalize direction
        distance = max(abs(direction_x), abs(direction_y))
        if distance > 0:
            self.character.velocity.x = direction_x / distance
            self.character.velocity.y = direction_y / distance

        # Move character
        movement_speed = 2  # Faster speed for walking to the door
        self.character.rect.x += self.character.velocity.x * movement_speed
        self.character.rect.y += self.character.velocity.y * movement_speed

        # Check if the character reached the door
        if self.character.rect.colliderect(self.door_rect):
            self.walk_to_door = False  # Stop walking
            self.transition_to_sport_mode = True  # Start transition
            self.door_index = 1  # Open door animation
            self.door = pygame.transform.scale(self.door_sprites[self.door_index], (130, 200))  # Open door animation
            self.door_open_timer = pygame.time.get_ticks()  # Start door open timer

    def handle_walk_to_learnroom(self):
        self.character.disable_movement = True
        self.character.force_animation("walk_right")

        # Move character toward the right edge of the screen
        movement_speed = 2
        self.character.rect.x += movement_speed

        # Check if character has reached the right edge
        if self.character.rect.right >= 600:  # Assuming screen width is 600
            self.walk_to_learnroom = False
            self.transition_to_learn_mode = True

    def update(self, dt):
        if not self.character.dragging:
            self.character.update(dt)

        if self.falling:
            self.everything_falls()

        if self.walk_to_window:
            self.handle_walk_to_window()

        if self.walk_to:
            self.handle_walk_to()

        if not self.walk_to_window and self.movement_resume_timer > 0:
            self.movement_resume_timer -= dt
            if self.movement_resume_timer <= 0:
                self.movement_resume_timer = 0
                self.character.disable_movement = False  # Resume movement

        if self.walk_to_learnroom:
            self.handle_walk_to_learnroom()
        
        if self.transition_to_learn_mode:
            self.scene_manager.set_scene(Lernzimmer(self.scene_manager))

        if self.walk_to_door:
            self.handle_walk_to_door()

            # Handle door open timer and transition
        if self.transition_to_sport_mode:
            if pygame.time.get_ticks() - self.door_open_timer > 1000:  # 2-second delay
                # wechsel zum joggen
                self.scene_manager.set_scene(JoggenScene(self.scene_manager))

        # Update weather every 5 minutes
        if pygame.time.get_ticks() - self.last_weather_update > 300000:  # 5 minutes in milliseconds
            self.update_weather()
            self.last_weather_update = pygame.time.get_ticks()

    def render(self, screen, debug_mode=False):
        # Hintergrund rendern
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.window, self.window_rect)
        screen.blit(self.door, self.door_rect)

        # Charakter und Sofa-Logik
        character_rect = self.character.rect
        if character_rect.bottom <= self.sofa_rect.centery:
            self.character.render(screen)
            screen.blit(self.sofa_image, self.sofa_rect)
        else:
            screen.blit(self.sofa_image, self.sofa_rect)
            self.character.render(screen)

        # Stehlampe
        screen.blit(self.standing_lamp, self.standing_lamp_rect)

        # Zeit und Wetter rendern
        current_time = datetime.now().strftime("%A %H:%M")
        time_surface = self.message_font_uhrzeit.render(f"{current_time}", False, (255, 255, 255))
        weather_surface = self.message_font.render(self.weather_info, False, (255, 255, 255))
        screen.blit(time_surface, (20, 20))
        screen.blit(weather_surface, (20, 60))

        # Szene auf den Kopf stellen, falls aktiviert
        if self.falling:
            flipped_screen = pygame.transform.flip(screen, False, True)  # Vertikales Spiegeln
            screen.blit(flipped_screen, (0, 0))

        if debug_mode:
            # Window debug info
            draw_debug_info(
                screen,
                self.window_rect,
                f"X: {self.window_rect.x}, Y: {self.window_rect.y}",
                self.debug_font
            )

            # door debug info
            draw_debug_info(
                screen,
                self.door_rect,
                f"X: {self.door_rect.x}, Y: {self.door_rect.y}",
                self.debug_font
            )

            # door index info
            draw_debug_info(
                screen,
                self.door_rect,
                f"Index: {self.door_index}",
                self.debug_font,
                text_offset=(0, self.door_rect.height + 5)
            )

            # lamp debug info
            draw_debug_info(
                screen,
                self.standing_lamp_rect,
                f"X: {self.standing_lamp_rect.x}, Y: {self.standing_lamp_rect.y}",
                self.debug_font
            )

            # lamp index info
            draw_debug_info(
                screen,
                self.standing_lamp_rect,
                f"Index: {self.current_weather_index}",
                self.debug_font,
                text_offset=(0, self.standing_lamp_rect.height + 5)
            )

            # window current index
            draw_debug_info(
                screen,
                self.window_rect,
                f"Index: {self.current_weather_index}",
                self.debug_font,
                text_offset=(0, self.window_rect.height + 5)
            )

            # Background debug info (text inside rect)
            draw_debug_info(
                screen,
                self.bg_rect,
                f"Tag/Nacht: {self.current_weather_index}",
                self.debug_font,
                text_offset=(5, 5)  # Inside the rect
            )

            # draw red box on walking ground
            pygame.draw.rect(screen, (255, 0, 0), (0, 346, 600, 600), 2)


            # Sofa debug info
            draw_debug_info(
                screen,
                self.sofa_rect,
                f"X: {self.sofa_rect.x}, Y: {self.sofa_rect.y}",
                self.debug_font
            )

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




