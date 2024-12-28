from character.animated_character import AnimatedCharacter
from Items import Item

import pygame
from scenes.sport_mode import SportModeScene
import requests
from datetime import datetime

API_KEY = "df2aff53d4447b60a08c391650e58d32"
CITY = "Wiesbaden"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=de"

class MainScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        # Time and weather setup
        self.message_font = pygame.font.SysFont('system-ui', 40)
        self.message_font_uhrzeit = pygame.font.SysFont('system-ui', 40)
        self.weather_info = "Loading weather..."
        self.last_weather_update = pygame.time.get_ticks()
        self.update_weather()

        # Clock setup
        self.clock = pygame.time.Clock()

        # Background
        self.background = pygame.image.load("assets/backgrounds/wohnzimmer.png").convert()
        self.background = pygame.transform.scale(self.background, (600, 600))

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

    def update(self, dt):
        if not self.character.dragging:
            self.character.update(dt)

        if self.walk_to_window:
            self.character.disable_movement = True
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

                # start random walking again
                #self.character.disable_movement = False


        if self.walk_to_door:
            self.character.disable_movement = True
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
                self.door_index = 1 # Open door animation
                self.door = pygame.transform.scale(self.door_sprites[self.door_index], (130, 200)) # Open door animation
                self.door_open_timer = pygame.time.get_ticks()  # Start door open timer

            # Handle door open timer and transition
        if self.transition_to_sport_mode:
            if pygame.time.get_ticks() - self.door_open_timer > 1000:  # 2-second delay
                self.scene_manager.set_scene(SportModeScene(self.scene_manager))

        # Update weather every 5 minutes
        if pygame.time.get_ticks() - self.last_weather_update > 300000:  # 5 minutes in milliseconds
            self.update_weather()
            self.last_weather_update = pygame.time.get_ticks()


    def render(self, screen):
        # Background render
        #screen.blit(self.background, (0, 0))

        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.window, self.window_rect)
        screen.blit(self.door, self.door_rect)


        # Determine layering: character behind or in front of sofa
        character_rect = self.character.rect
        if character_rect.bottom <= self.sofa_rect.centery:  # Compare with the sofa's vertical midpoint
            # Render character first (behind sofa)
            self.character.render(screen)
            screen.blit(self.sofa_image, self.sofa_rect)
        else:
            # Render sofa first (in front of character)
            screen.blit(self.sofa_image, self.sofa_rect)
            self.character.render(screen)


        # Standinglamp
        screen.blit(self.standing_lamp, self.standing_lamp_rect)

        # Render time and weather
        current_time = datetime.now().strftime("%A %H:%M")
        time_surface = self.message_font_uhrzeit.render(f"{current_time}", False, (255, 255, 255))
        weather_surface = self.message_font.render(self.weather_info, False, (255, 255, 255))
        screen.blit(time_surface, (20, 20))
        screen.blit(weather_surface, (20, 60))

