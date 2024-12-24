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
        self.message_font = pygame.font.Font(None, 40)
        self.weather_info = "Loading weather..."
        self.last_weather_update = pygame.time.get_ticks()
        self.update_weather()

        # Clock setup
        self.clock = pygame.time.Clock()

        # Background
        self.background = pygame.image.load("assets/backgrounds/wohnzimmer.png").convert()
        self.background = pygame.transform.scale(self.background, (600, 600))

        self.bg_sprites = Item("assets/spritesheets/florrwall.png", 64, 112, 1, 4)
        # Scale the first sprite from the list
        self.bg = pygame.transform.scale(self.bg_sprites[2], (600, 600))
        # Create a rect for positioning
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Sofa
        self.sofa_image = pygame.image.load("assets/models/sofa.png").convert_alpha()
        self.sofa_image = pygame.transform.scale(self.sofa_image, (268, 170))  # Scale the sofa
        self.sofa_rect = self.sofa_image.get_rect(topleft=(107, 345))

        # Character
        self.character = AnimatedCharacter(373, 549)
        self.last_click_time = 0

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
            else:
                self.weather_info = "Fehler beim Laden der Wetterdaten."
        except Exception as e:
            self.weather_info = "Keine Wetterdaten verfügbar."

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Print the click position
            self.print_click_position(event)

            #doppeltklick
            current_time = pygame.time.get_ticks()
            if current_time - self.last_click_time < 300:  # Detect double-click
                self.scene_manager.set_scene(SportModeScene(self.scene_manager))
            self.last_click_time = current_time

    def update(self, dt):
        self.character.update(dt)

        # Update weather every 5 minutes
        if pygame.time.get_ticks() - self.last_weather_update > 300000:  # 5 minutes in milliseconds
            self.update_weather()
            self.last_weather_update = pygame.time.get_ticks()


    def render(self, screen):
        # Background render
        #screen.blit(self.background, (0, 0))

        screen.blit(self.bg, self.bg_rect)


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

        # Render time and weather
        current_time = datetime.now().strftime("%H:%M")
        time_surface = self.message_font.render(f"{current_time}", True, (255, 255, 255))
        weather_surface = self.message_font.render(self.weather_info, True, (255, 255, 255))
        screen.blit(time_surface, (20, 20))
        screen.blit(weather_surface, (20, 60))

