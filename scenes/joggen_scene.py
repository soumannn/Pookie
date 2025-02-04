import pygame, requests
from Items import Item
from character.animated_character import AnimatedCharacter
from helper.debug_box import draw_debug_info
from config import WEATHER_URL
from datetime import datetime


class JoggenScene:
    def __init__(self, scene_manager, pookie):
        self.scene_manager = scene_manager
        self.pookie = pookie

        # set false so we can go back!
        self.pookie.transition_to_sport_mode = False


        self.start_time = pygame.time.get_ticks()

        # Debug font
        self.debug_font = pygame.font.Font(None, 24)

        self.day_night =  0  # Default to day
        self.last_weather_update = pygame.time.get_ticks()

        # Load city skyline images for day and night
        self.city_layers_day = [
            {"image": self.pookie.apply_cozy_solo(pygame.image.load("assets/spritesheets/citybg/city_5/2.png")).convert_alpha(), "y": -20, "speed": 0.5, "x": 0},
            {"image": self.pookie.apply_cozy_solo(pygame.image.load("assets/spritesheets/citybg/city_5/3.png")).convert_alpha(), "y": -00, "speed": 1.0, "x": 0},
            {"image": self.pookie.apply_cozy_solo(pygame.image.load("assets/spritesheets/citybg/city_5/4.png")).convert_alpha(), "y": 17, "speed": 1.5, "x": 0},
            {"image": self.pookie.apply_cozy_solo(pygame.image.load("assets/spritesheets/citybg/city_5/5.png")).convert_alpha(), "y": 17, "speed": 2.0, "x": 0},
        ]
        self.city_layers_night = [
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/2.png").convert_alpha(), "y": 17, "speed": 0.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/3.png").convert_alpha(), "y": 17, "speed": 1.0, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/4.png").convert_alpha(), "y": 17, "speed": 1.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/5.png").convert_alpha(), "y": 17, "speed": 2.0, "x": 0}
        ]

        # Load and scale the street background
        self.street_image = pygame.image.load("assets/spritesheets/citybg/city_5/street.png").convert_alpha()
        self.street_image = pygame.transform.scale(self.street_image, (600, 10))  # Adjust height if needed
        self.street_x = 0  # Initial x position
        self.street_speed = 4 # Movement speed

        # Set initial city layers to day
        self.city_layers = self.city_layers_day

        # Background
        self.bg_sprites = Item("assets/spritesheets/newBg.png", 64, 112, 1, 6)
        self.bg = pygame.transform.scale(self.bg_sprites[4], (640, 590))
        self.cozy_bg = self.pookie.apply_cozy_solo(self.bg.copy())
        self.bg_rect = self.cozy_bg.get_rect(topleft=(0, 0))

        # Character setup
        if not self.pookie.has_unlocked_car:
            self.character = AnimatedCharacter(0, 346)  # Start at the left edge
            self.character.disable_movement = True
            self.character.current_animation = "walk_right"  # Walk animation
        else:
            self.wheel_rotation = 0  # Track the rotation angle
            self.car_speed = 2
            self.auto_frame = pygame.image.load("assets/car/auto.png").convert_alpha()
            self.auto_frame = pygame.transform.scale(self.auto_frame, (240, 100))
            self.auto_rect =  self.auto_frame.get_rect(topleft=(20, 310))

            self.auto_left_tire = pygame.image.load("assets/car/reifenLinks.png").convert_alpha()
            self.auto_left_tire = pygame.transform.scale(self.auto_left_tire, (37, 37))
            self.auto_left_tire_rect = self.auto_left_tire.get_rect(topleft=(45, 360))

            self.auto_right_tire = pygame.image.load("assets/car/reifenRechts.png").convert_alpha()
            self.auto_right_tire = pygame.transform.scale(self.auto_right_tire, (37, 37))
            self.auto_right_tire_rect = self.auto_right_tire.get_rect(topleft=(200, 360))

            self.auto_left_tire_rotated = self.auto_left_tire.copy()
            self.auto_right_tire_rotated = self.auto_right_tire.copy()

        self.update_weather()

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
                self.set_day_night()
            else:
                self.weather_info = "Fehler beim Laden der Wetterdaten."
        except Exception as e:
            self.weather_info = "Keine Wetterdaten verfügbar."

    def set_day_night(self):
        """Set day or night based on sunrise and sunset times."""
        try:
            current_time = datetime.now().timestamp()
            if self.sunrise <= current_time < self.sunset:
                self.day_night = 0  # Day
                self.city_layers = self.city_layers_day
            else:
                self.day_night = 1  # Night
                self.city_layers = self.city_layers_night
                newBg = pygame.transform.scale(self.bg_sprites[5], (640, 590))
                self.cozy_bg = self.pookie.apply_cozy_solo(newBg.copy())

        except AttributeError:
            # Default to day if sunrise/sunset not available
            self.day_night = 0
            self.city_layers = self.city_layers_day

    def update(self, dt):
        if self.pookie.has_unlocked_car:
            time = 5000
        else:
            time = 6000

        if pygame.time.get_ticks() - self.start_time >= time:  # 4000 ms = 4 seconds
            self.pookie.walk_to_gym = True

        if self.pookie.walk_to_gym:
            self.pookie.handle_walk_to_gym()

        # Update weather every 5 minutes
        if pygame.time.get_ticks() - self.last_weather_update > 300000:  # 5 minutes in milliseconds
            self.update_weather()
            self.last_weather_update = pygame.time.get_ticks()

        # Scroll each city layer
        for layer in self.city_layers:
            layer["x"] -= layer["speed"]
            if layer["x"] <= -600:  # Reset position for seamless scrolling
                layer["x"] = 0

        # Scroll the street background
        self.street_x -= self.street_speed
        if self.street_x <= -600:  # Reset position for seamless scrolling
            self.street_x = 0

        if not self.pookie.has_unlocked_car:
            # Move the character to the right
            movement_speed = 2  # Character walking speed
            self.character.rect.x += movement_speed

            # Loop character position if they reach the screen edge
            if self.character.rect.x > 600:
                self.character.rect.x = -self.character.rect.width

            # Update the character animation
            self.character.update(dt)

        if self.pookie.has_unlocked_car:
            # Move the entire car forward
            self.auto_rect.x += self.car_speed

            # Rotate the wheels continuously
            self.wheel_rotation -= 10  # Adjust rotation speed
            self.auto_left_tire_rotated = pygame.transform.rotate(self.auto_left_tire, self.wheel_rotation)
            self.auto_right_tire_rotated = pygame.transform.rotate(self.auto_right_tire, self.wheel_rotation)

            # Keep the wheels moving with the car
            self.auto_left_tire_rect = self.auto_left_tire_rotated.get_rect(center=(self.auto_rect.x + 45, 380))
            self.auto_right_tire_rect = self.auto_right_tire_rotated.get_rect(center=(self.auto_rect.x + 195, 380))

            # Reset car position if it moves off the screen
            if self.auto_rect.x > 600:
                self.auto_rect.x = -self.auto_rect.width

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln
                from scenes.wohnzimmer_scene import Wohnzimmer
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager, self.pookie, 55, 206))


    def initialize_state(self):
        """Helper function to initialize scene state."""
        print("trying to reset..")
        self.pookie.character.disable_movement = False

    def render(self, screen, debug_mode=False):
        screen.blit(self.cozy_bg, self.bg_rect)

        for layer in self.city_layers:
            screen.blit(layer["image"], (layer["x"], layer["y"]))  # First part
            screen.blit(layer["image"], (layer["x"] + 600, layer["y"]))

        # Render the scrolling street at the bottom
        screen.blit(self.street_image, (self.street_x, 420))  # First copy
        screen.blit(self.street_image, (self.street_x + 600, 420))  # Looping part

        if not self.pookie.has_unlocked_car:
            self.character.render(screen)
        else:
            screen.blit(self.auto_frame, self.auto_rect)
            screen.blit(self.auto_left_tire_rotated, self.auto_left_tire_rect)
            screen.blit(self.auto_right_tire_rotated, self.auto_right_tire_rect)


