import pygame, requests
from Items import Item
from character.animated_character import AnimatedCharacter
from helper.debug_box import draw_debug_info
from config import WEATHER_URL
from datetime import datetime


class JoggenScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.message_font = pygame.font.Font(None, 40)
        self.message = self.message_font.render("Sport Mode!", True, (255, 255, 255))

        # Debug font
        self.debug_font = pygame.font.Font(None, 24)

        self.day_night =  0  # Default to day
        self.last_weather_update = pygame.time.get_ticks()

        # Load city skyline images for day and night
        self.city_layers_day = [
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/2.png").convert_alpha(), "y": -40, "speed": 0.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/3.png").convert_alpha(), "y": -20, "speed": 1.0, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/4.png").convert_alpha(), "y": 20, "speed": 1.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_5/5.png").convert_alpha(), "y": 20, "speed": 2.0, "x": 0}
        ]
        self.city_layers_night = [
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/2.png").convert_alpha(), "y": -45, "speed": 0.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/3.png").convert_alpha(), "y": -20, "speed": 1.0, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/4.png").convert_alpha(), "y": 20, "speed": 1.5, "x": 0},
            {"image": pygame.image.load("assets/spritesheets/citybg/city_1/5.png").convert_alpha(), "y": 20, "speed": 2.0, "x": 0}
        ]

        # Set initial city layers to day
        self.city_layers = self.city_layers_day

        # Background
        self.bg_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        self.bg = pygame.transform.scale(self.bg_sprites[4], (600, 600))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Character setup
        self.character = AnimatedCharacter(0, 346)  # Start at the left edge
        self.character.disable_movement = True
        self.character.current_animation = "walk_right"  # Walk animation

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
        except AttributeError:
            # Default to day if sunrise/sunset not available
            self.day_night = 0
            self.city_layers = self.city_layers_day

    def update(self, dt):
        # Update weather every 5 minutes
        if pygame.time.get_ticks() - self.last_weather_update > 300000:  # 5 minutes in milliseconds
            self.update_weather()
            self.last_weather_update = pygame.time.get_ticks()

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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln
                from scenes.wohnzimmer_scene import Wohnzimmer
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager))

    def render(self, screen, debug_mode=False):
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.message, (200, 100))

        for layer in self.city_layers:
            screen.blit(layer["image"], (layer["x"], layer["y"]))  # First part
            screen.blit(layer["image"], (layer["x"] + 600, layer["y"]))

        self.character.render(screen)

        if debug_mode:
            # draw city layers debug info
            for layer in self.city_layers:
                draw_debug_info(
                    screen,
                    pygame.Rect(layer["x"], layer["y"], 600, 600),
                    f"X: {layer['x']}, Y: {layer['y']}",
                    self.debug_font,
                    text_offset=(550, 0)
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

            # draw red box on walking ground
            pygame.draw.rect(screen, (255, 0, 0), (0, 346, 600, 600), 2)

            # debug info about weather and day
            draw_debug_info(
                screen,
                pygame.Rect(0, 0, 600, 20),
                f"{self.day_night}",
                self.debug_font,
                text_offset=(0, 0)
            )

            # last weather update
            draw_debug_info(
                screen,
                pygame.Rect(0, 20, 600, 20),
                f"Last update: {self.last_weather_update}",
                self.debug_font,
                text_offset=(0, 0)
            )

            # city layer debug info
            draw_debug_info(
                screen,
                pygame.Rect(0, 40, 600, 20),
                f"City layer: {self.city_layers[0].items()}",
                self.debug_font,
                text_offset=(0, 0)
            )
