import time

from Items import Item
from helper.debug_box import draw_debug_info


import pygame

import requests
from datetime import datetime
from config import WEATHER_URL



class Wohnzimmer:
    def __init__(self, scene_manager, pookie, pookiePosX=0, pookiePosY=0):
        self.scene_manager = scene_manager
        self.pookie = pookie


        self.start_time = time.time()
        self.message_shown = 0

        #self.pookie.startDetectionThread()
        self.pookie.character.disable_movement = False
        self.pookie.character.force_animation("walk_left")

        # Character
        #self.character = AnimatedCharacter(373, 549)
        self.last_click_time = 0
        self.dragging_character = False

        #waste
        self.waste = self.pookie.apply_cozy_solo(pygame.image.load("assets/models/waste.png")).convert_alpha()
        self.waste = pygame.transform.scale(self.waste, (200, 200))
        self.waste_rect = self.waste.get_rect(topleft=(150, 350))

        # debug-font
        self.debug_font = pygame.font.Font(None, 24)


        self.tilt_detected = False

        #sensor temp
        self.sensor_temp = 0

        self.falling = False
        self.fall_speed = 5  # Geschwindigkeit des Fallens
        self.scene_flipped = False  # Tracks whether the scene is flipped


        self.movement_resume_timer = 0
        self.resume_movement_delay = 500  # 500ms delay before resuming random movement

        # Zielpositionen für fallende Objekte
        self.character_target_y = 320
        self.window_target_y = 320
        self.door_target_y = 320
        self.sofa_target_y = 320
        self.lamp_target_y = 320

        # Time and weather setup
        self.font = pygame.font.Font('assets/zh-cn.ttf', 24)
        #self.message_font = pygame.font.SysFont('system-ui', 40)
        self.message_font_uhrzeit = pygame.font.Font('assets/zh-cn.ttf', 40)
        self.weather_info = "Loading weather..."
        self.last_weather_update = pygame.time.get_ticks()
        self.update_weather()

        self.bg_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        # Scale the first sprite from the list
        self.bg = pygame.transform.scale(self.bg_sprites[2], (640, 480))
        # Create a rect for positioning
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))
        self.cozy_bg = self.pookie.apply_cozy_effect(self.bg.copy())

        # Windows
        self.current_weather_index = 0
        self.window_sprites = Item("assets/spritesheets/windows.png", 32, 28, 1, 4)
        self.window = pygame.transform.scale(self.window_sprites[self.current_weather_index], (130, 130))
        self.window_rect = self.window.get_rect(topleft=(210, 60))
        self.cozy_window = self.pookie.apply_cozy_solo(self.window.copy())
        self.walk_to_window = False

        #treppe
        self.treppe = self.pookie.apply_cozy_solo(pygame.image.load("assets/models/treppe.png")).convert_alpha()
        self.treppe = pygame.transform.scale(self.treppe, (260, 320))
        self.treppe_rect = self.treppe.get_rect(topleft=(385, -10))

        #teppich
        self.teppich = self.pookie.apply_cozy_solo(pygame.image.load("assets/models/teppich.png")).convert_alpha()
        self.teppich = pygame.transform.scale(self.teppich, (350, 200))
        self.teppich_rect = self.teppich.get_rect(topleft=(280, 336))

        #plattenspieler
        self.plattenspieler = self.pookie.apply_cozy_solo(pygame.image.load("assets/models/plattenspieler.png")).convert_alpha()
        self.plattenspieler = pygame.transform.scale(self.plattenspieler, (120, 120))
        self.plattenspieler_rect = self.plattenspieler.get_rect(topleft=(140, 300))

        # Sofa
        self.sofa_image = pygame.image.load("assets/models/sofa.png").convert_alpha()
        self.sofa_image = pygame.transform.scale(self.sofa_image, (250, 150))  # Scale the sofa
        self.sofa_rect = self.sofa_image.get_rect(topleft=(300, 270))
        self.cozy_sofa = self.pookie.apply_cozy_solo(self.sofa_image.copy())

        # State for transitioning to sport mode (Walk to Door)
        self.door_index = 0

        # Door
        self.door_sprites = Item("assets/spritesheets/doors.png", 30, 51, 1, 3)
        self.door = pygame.transform.scale(self.door_sprites[self.door_index], (120, 200))
        self.door_rect = self.door.get_rect(topleft=(30, 88))
        self.cozy_door = self.pookie.apply_cozy_solo(self.door.copy())

        # Standinglamp
        self.stand_lamp_sprites = Item("assets/spritesheets/standinglamps.png", 15, 46, 1, 2)
        self.standing_lamp = pygame.transform.scale(self.stand_lamp_sprites[self.current_weather_index], (60, 180))
        self.standing_lamp_rect = self.standing_lamp.get_rect(topleft=(560, 290))
        self.cozy_lamp = self.pookie.apply_cozy_solo(self.standing_lamp.copy())

        self.shake_timer = None

        self.set_day_night()

        self.pookie.character.setPosition(pookiePosX, pookiePosY)

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

            self.cozy_window = pygame.transform.scale(self.pookie.apply_cozy_solo(self.window_sprites[self.current_weather_index]), (130, 130))
            self.cozy_lamp = pygame.transform.scale(self.pookie.apply_cozy_solo(self.stand_lamp_sprites[self.current_weather_index]), (60, 180))

        except AttributeError:
            # Default to day if sunrise/sunset not available
            self.current_weather_index = 0

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
                self.cozy_window = pygame.transform.scale(self.pookie.apply_cozy_solo(self.window_sprites[self.current_weather_index]), (130, 130))

            # Detect character drag
            if self.pookie.character.rect.collidepoint(event.pos):  # Start dragging
                print("picking up....")
                self.pookie.character.disable_movement = True
                self.dragging_character = True
                self.pookie.character.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_character:  # Stop dragging
                print("let go")
                self.pookie.character.disable_movement = False
                self.dragging_character = False
                self.pookie.character.dragging = False
                self.pookie.character.snap_to_grid()  # Snap back to the allowed grid

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_character:  # Update position while dragging
                print("dragging..")
                self.pookie.character.set_position(event.pos[0] - self.pookie.character.rect.width // 2,
                                            event.pos[1] - self.pookie.character.rect.height // 2)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                # Use an index to toggle
                self.current_weather_index = 1 - self.current_weather_index  # Toggles between 0 and 1
                self.cozy_window = pygame.transform.scale(self.pookie.apply_cozy_solo(self.window_sprites[self.current_weather_index]), (130, 130))
                self.cozy_lamp = pygame.transform.scale(self.pookie.apply_cozy_solo(self.stand_lamp_sprites[self.current_weather_index]),
                                                            (60, 180))
            elif event.key == pygame.K_s:
                self.pookie.walk_to_door = True  # Start walking to the door

            elif event.key == pygame.K_o:
                self.walk_to_window = True

            elif event.key == pygame.K_h:
                self.pookie.character.disable_movement = True
                self.pookie.character.force_animation("hantel")

            elif event.key == pygame.K_g:
                self.pookie.walk_to_gym = True

            elif event.key == pygame.K_t:
                """TikTok Modus
                Walk to (426, 453) and switch to 'handy_modus'."""
                self.pookie.character.disable_movement = True
                self.pookie.walk_to_animation = "handy_modus"

                #self.walk_to = True
                self.pookie.walk_to = True

                self.pookie.walk_to_target = (448, 303)  # Target position for TikTok mode (244, 190)
                self.pookie.handy += 1
                self.pookie.letPookieSay(self.pookie.tikTokMessage())
            elif event.key == pygame.K_l:
                self.pookie.character.setPosition(55, 206)
            elif event.key == pygame.K_a:
                self.pookie.triggerAutoEvent()

            elif event.key == pygame.K_b:
                """Buch lesen Modus"""
                self.pookie.walk_to_learnroom = True
                self.pookie.learn += 1
                # print(f'{self.pookie.learn} {self.pookie.handy}')
                self.pookie.letPookieSay(self.pookie.bookMessage())


            elif event.key == pygame.K_DOWN:  # Pfeil nach unten
                self.falling = True
                self.flip_scene()

            elif event.key == pygame.K_r:  # Zurücksetzen
                self.initialize_state()
                    #self.falling = False
                    #self.reset_positions()

    def reset_positions(self):
        self.pookie.character.rect.y = 0
        self.window_rect.y = 32
        self.door_rect.y = 160
        self.sofa_rect.y = 365
        self.standing_lamp_rect.y = 376

    def flip_scene(self):
        """Flip the entire scene upside down, including bounds."""
        self.scene_flipped = not self.scene_flipped
        self.pookie.character.flip_bounds(self.scene_flipped)

    def everything_falls(self):
        """Make all objects in the scene fall (including character)."""
        # Character falls
        if self.scene_flipped:
            if self.pookie.character.rect.top > 0:
                self.pookie.character.rect.y -= self.fall_speed
            else:
                self.pookie.character.rect.y = 0
        else:
            if self.pookie.character.rect.bottom < 320:
                self.pookie.character.rect.y += self.fall_speed
            else:
                self.pookie.character.rect.y = 320 - self.pookie.character.rect.height

        # Window falls
        if self.scene_flipped:
            if self.window_rect.top > 0:
                self.window_rect.y -= self.fall_speed
            else:
                self.window_rect.y = 0
        else:
            if self.window_rect.bottom < 320:
                self.window_rect.y += self.fall_speed
            else:
                self.window_rect.y = 320 - self.window_rect.height

        # Door falls
        if self.scene_flipped:
            if self.door_rect.top > 0:
                self.door_rect.y -= self.fall_speed
            else:
                self.door_rect.y = 0
        else:
            if self.door_rect.bottom < 320:
                self.door_rect.y += self.fall_speed
            else:
                self.door_rect.y = 320 - self.door_rect.height

        # Sofa falls
        if self.scene_flipped:
            if self.sofa_rect.top > 0:
                self.sofa_rect.y -= self.fall_speed
            else:
                self.sofa_rect.y = 0
        else:
            if self.sofa_rect.bottom < 320:
                self.sofa_rect.y += self.fall_speed
            else:
                self.sofa_rect.y = 320 - self.sofa_rect.height

        # Lamp falls
        if self.scene_flipped:
            if self.standing_lamp_rect.top > 0:
                self.standing_lamp_rect.y -= self.fall_speed
            else:
                self.standing_lamp_rect.y = 0
        else:
            if self.standing_lamp_rect.bottom < 320:
                self.standing_lamp_rect.y += self.fall_speed
            else:
                self.standing_lamp_rect.y = 320 - self.standing_lamp_rect.height

    def handle_walk_to_window(self):
        if self.walk_to_window:
            self.pookie.character.disable_movement = True
            self.pookie.character.force_animation("walk_up")
            window_center = self.window_rect.center
            character_center = self.pookie.character.rect.center

            direction_x = window_center[0] - character_center[0]
            direction_y = window_center[1] - character_center[1]

            # Normalize direction
            distance = max(abs(direction_x), abs(direction_y))
            if distance > 0:
                self.pookie.character.velocity.x = direction_x / distance
                self.pookie.character.velocity.y = direction_y / distance

            # Move character
            movement_speed = 2  # Faster speed for walking to the door
            self.pookie.character.rect.x += self.pookie.character.velocity.x * movement_speed
            self.pookie.character.rect.y += self.pookie.character.velocity.y * movement_speed

            if self.pookie.character.rect.colliderect(self.window_rect):
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
                self.window = pygame.transform.scale(self.pookie.apply_cozy_solo(self.window_sprites[self.current_weather_index]), (130, 130))

                # Start movement resume timer
                self.movement_resume_timer = self.resume_movement_delay

    def handle_walk_to_door(self):
        self.pookie.character.disable_movement = True
        self.pookie.character.force_animation("walk_left")
        # Move character toward the door
        door_center = self.door_rect.center
        character_center = self.pookie.character.rect.center

        # Calculate direction
        direction_x = door_center[0] - character_center[0]
        direction_y = door_center[1] - character_center[1]

        # Normalize direction
        distance = max(abs(direction_x), abs(direction_y))
        if distance > 0:
            self.pookie.character.velocity.x = direction_x / distance
            self.pookie.character.velocity.y = direction_y / distance

        # Move character
        movement_speed = 2  # Faster speed for walking to the door
        self.pookie.character.rect.x += self.pookie.character.velocity.x * movement_speed
        self.pookie.character.rect.y += self.pookie.character.velocity.y * movement_speed

        # Check if the character reached the door
        if self.pookie.character.rect.colliderect(self.door_rect):
            self.pookie.walk_to_door = False  # Stop walking
            self.pookie.transition_to_sport_mode = True  # Start transition
            self.door_index = 1  # Open door animation
            self.cozy_door = pygame.transform.scale(self.pookie.apply_cozy_solo(self.door_sprites[self.door_index]), (120, 200))  # Open door animation


    """
    def perform_animation(self, animation_name: str, target: tuple, message: str=""):

        print(f"Performing animation '{animation_name}' to target {target}")
        if len(message) > 0:
            self.pookie.letPookieSay(message)
        self.walk_to_animation = animation_name
        self.pookie.walk_to_target = target
        #self.walk_to = True
        self.pookie.walk_to = True
        self.pookie.character.disable_movement = True
    """

    def initialize_state(self):
        """Helper function to initialize scene state."""
        print("trying to reset..")
        self.pookie.character.disable_movement = False



    def update(self, dt):
        self.pookie.check_shake()

        elapsed_time = time.time() - self.start_time
        fade_duration = 8  # Sekunden bevor das Fading beginnt
        fade_out_time = 2  # Sekunden für den Fade-out-Effekt

        if not self.pookie.feedforward:
            current_time = datetime.now().strftime("%A %H:%M")

            # Erste Nachricht nach 0 Sekunden
            if self.message_shown == 0 and elapsed_time > 0:
                self.pookie.letPookieSay("Hallo ich bin Pookie. Nimm mich in deinem Alltag mit und bring mir was bei!",
                                         5000)
                self.message_shown = 1  # Fortschritt speichern

            # Zweite Nachricht nach 4 Sekunden
            if self.message_shown == 1 and elapsed_time > fade_duration:
                self.pookie.letPookieSay("Nimm doch mal dein Handy in die Hand.. und adde mich auf tiktok @pookie3", 5000)
                self.message_shown = 2  # Fortschritt speichern

                self.pookie.feedforward = True

        # Handle shake timer to re-enable movement
        if self.shake_timer is not None:
            if pygame.time.get_ticks() - self.shake_timer >= 3000:  # 3 seconds
                self.pookie.character.disable_movement = False
                self.shake_timer = None  # Reset the timer

        if not self.pookie.character.dragging:
            self.pookie.character.update(dt)

        if self.pookie.walk_to_gym:
            self.pookie.handle_walk_to_gym()

        if self.falling:
            self.everything_falls()

        if self.walk_to_window:
            self.handle_walk_to_window()

        if self.pookie.walk_to:
            self.pookie.handle_walk_to()

        if self.pookie.walk_to_learnroom:
            self.pookie.handle_walk_to_learnroom()


        if not self.walk_to_window and self.movement_resume_timer > 0:
            self.movement_resume_timer -= dt
            if self.movement_resume_timer <= 0:
                self.movement_resume_timer = 0
                self.pookie.character.disable_movement = False  # Resume movement


        if self.pookie.walk_to_door:
            self.handle_walk_to_door()

            # Handle door open timer and transition
        if self.pookie.transition_to_sport_mode:
            self.scene_manager.set_scene(self.scene_manager.scenes[2](self.scene_manager, self.pookie))

        # Update weather every 5 minutes
        #if pygame.time.get_ticks() - self.last_weather_update > 300000:  # 5 minutes in milliseconds
        #    self.update_weather()
        #    self.last_weather_update = pygame.time.get_ticks()

        #if self.is_walking_to_learnroom:
        #    self.handle_walk_to_learnroom()

    def render(self, screen, debug_mode=False):
        # Hintergrund rendern
        screen.blit(self.cozy_bg, self.bg_rect)
        screen.blit(self.cozy_window, self.window_rect)
        screen.blit(self.cozy_door, self.door_rect)
        screen.blit(self.treppe, self.treppe_rect)
        screen.blit(self.teppich, self.teppich_rect)

        #waste
        if self.pookie.handy > 10:
            screen.blit(self.waste, self.waste_rect)


        screen.blit(self.cozy_lamp, self.standing_lamp_rect)


        character_rect = self.pookie.character.rect
        if character_rect.bottom <= self.sofa_rect.centery:
            self.pookie.character.render(screen)
            screen.blit(self.cozy_sofa, self.sofa_rect)
        else:
            screen.blit(self.cozy_sofa, self.sofa_rect)
            self.pookie.character.render(screen)


        # Zeit und Wetter rendern
        elapsed_time = time.time() - self.start_time
        fade_duration = 4  # Seconds before fading starts
        fade_out_time = 2  # Seconds for fade-out effect

        current_time = datetime.now().strftime("%A %H:%M")
        if elapsed_time < fade_duration + fade_out_time:
            alpha = 255  # Fully visible
            if elapsed_time > fade_duration:
                alpha = max(255 - int(((elapsed_time - fade_duration) / fade_out_time) * 255), 0)

            # Render text with alpha fading
            time_surface = self.message_font_uhrzeit.render(f"{current_time}", True, (255, 255, 255))
            weather_surface = self.font.render(self.weather_info, True, (255, 255, 255))

            # Apply alpha to surfaces
            time_surface.set_alpha(alpha)
            weather_surface.set_alpha(alpha)

            screen.blit(time_surface, (30, 360))
            screen.blit(weather_surface, (30, 410))

        # Szene auf den Kopf stellen, falls aktiviert
        if self.falling:
            flipped_screen = pygame.transform.flip(screen, False, True)  # Vertikales Spiegeln
            screen.blit(flipped_screen, (0, 0))

        if hasattr(self.pookie, "pookie_message_box"):
            if pygame.time.get_ticks() - self.pookie.message_display_time < self.pookie.message_duration:
                # Draw the white box
                screen.blit(self.pookie.pookie_message_box[0], self.pookie.pookie_message_box[1])

                # Draw the character image
                screen.blit(self.pookie.pookie_character_image[0], self.pookie.pookie_character_image[1])

                # Draw the text lines
                text_surfaces, text_start_pos = self.pookie.pookie_message_text
                x, y = text_start_pos
                for text_surface in text_surfaces:
                    screen.blit(text_surface, (x, y))
                    y += text_surface.get_height() + 5
            else:
                # Remove the message after the duration
                del self.pookie.pookie_message_box
                del self.pookie.pookie_message_text
                del self.pookie.pookie_character_image


        if debug_mode:
            # sensor temp
            """
            if IS_RASPBERRY_PI:
                temp_surface = self.message_font.render(f"PI temp: {self.sensor_temp:.1f}°C", False, (255, 255, 255))
                screen.blit(temp_surface, (20, 90))

                sensor_data = self.message_font.render(f"Sensor: {self.read_sensor_data()}", False, (255, 255, 255))
                screen.blit(sensor_data, (20, 120))
            """


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
            pygame.draw.rect(screen, (255, 0, 0), (0, 270, 640, 200), 2)


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
                self.pookie.character.rect,
                f"X: {self.pookie.character.rect.x}, Y: {self.pookie.character.rect.y}",
                self.debug_font,
                text_offset=(0, self.pookie.character.rect.height + 5)  # Below the rect
            )

            # Character status
            draw_debug_info(
                screen,
                self.pookie.character.rect,
                f"{self.pookie.character.current_animation}",
                self.debug_font,
                text_offset=(0, self.pookie.character.rect.height + 25)
            )

            # Autowalk status
            draw_debug_info(
                screen,
                self.pookie.character.rect,
                f"Autowalk {'off' if self.pookie.character.disable_movement else 'on'}",
                self.debug_font,
                text_offset=(0, self.pookie.character.rect.height + 45)
            )




