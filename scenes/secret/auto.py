import pygame
from scenes.wohnzimmer_scene import Wohnzimmer
import textwrap


class AutoEvent:
    def __init__(self, scene_manager, pookie):
        self.scene_manager = scene_manager
        self.pookie = pookie

        # Background
        self.bg = self.pookie.apply_cozy_solo(pygame.image.load("assets/backgrounds/unterdeneichen.png")).convert()
        self.bg = pygame.transform.scale(self.bg, (640, 480))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Gong
        self.gong = self.pookie.apply_cozy_solo(pygame.image.load("assets/models/gong.png")).convert_alpha()
        self.gong = pygame.transform.scale(self.gong, (300, 300))
        self.gong_rect = self.gong.get_rect(topleft=(150, 100))

        # Animation properties
        self.shaking = True         # Start shaking immediately
        self.shake_timer = 0        # Counter for shake duration
        self.shake_duration = 2000  # Total shake duration in milliseconds (2 seconds)
        self.shake_amplitude = 5    # How much it moves up/down
        self.shake_speed = 100      # How often (ms) the position changes
        self.last_shake_time = 0    # Tracks last shake update

        # Dialogue sequence tracking
        self.dialogue_stage = 0     # 0 = not started, 1 = first message, etc.
        self.dialogue_start_time = None  # Time when first dialogue starts

        # Font
        self.message_font = pygame.font.SysFont('system-ui', 40)

        # Fade-to-black effect
        self.fading = False
        self.fade_alpha = 0
        self.fade_surface = pygame.Surface((640, 480))
        self.fade_surface.fill((0, 0, 0))

    def letBerduxSay(self, message: str, duration: int = 5000):
        """Display a message from Berdux."""
        box_width = 640
        box_height = 130
        box_x = (640 - box_width) // 2
        box_y = 480 - box_height

        white_box = pygame.Surface((box_width, box_height))
        white_box.fill((255, 255, 255))

        wrapped_text = textwrap.wrap(message, width=30)
        text_surfaces = [self.message_font.render(line, True, (0, 0, 0)) for line in wrapped_text]

        character_image = pygame.image.load("assets/characters/berdux.png").convert_alpha()
        character_image = pygame.transform.scale(character_image, (150, 200))
        character_rect = character_image.get_rect(topleft=(box_x + 530, box_y - 60))

        self.pookie_message_box = (white_box, (box_x , box_y))
        self.pookie_message_text = (text_surfaces, (box_x + 20, box_y + 20))
        self.pookie_character_image = (character_image, character_rect)

        self.message_display_time = pygame.time.get_ticks()
        self.message_duration = duration

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        # Gong shaking effect
        if self.shaking:
            if current_time - self.last_shake_time > self.shake_speed:
                offset = self.shake_amplitude if (self.shake_timer // self.shake_speed) % 2 == 0 else -self.shake_amplitude
                self.gong_rect.y += offset
                self.last_shake_time = current_time
                self.shake_timer += self.shake_speed

            if self.shake_timer >= self.shake_duration:
                self.shaking = False
                self.gong = None
                self.dialogue_stage = 1  # Start the dialogue sequence
                self.letBerduxSay("Glückwunsch, Sie haben ihren Bachelor geschafft!")
                self.dialogue_start_time = current_time

        # Handle the dialogue sequence
        if self.dialogue_stage == 1 and current_time - self.dialogue_start_time >= 5000:
            self.pookie.letPookieSay("Ja es war gar nicht schwer!", 5000)
            self.dialogue_stage = 2
            self.dialogue_start_time = current_time

        elif self.dialogue_stage == 2 and current_time - self.dialogue_start_time >= 5000:
            self.letBerduxSay("Sie haben sich das verdient, hier haben Sie mein Auto!", 5000)
            self.dialogue_stage = 3
            self.dialogue_start_time = current_time

        elif self.dialogue_stage == 3 and current_time - self.dialogue_start_time >= 5000:
            self.fading = True  # Start fade to black
            self.dialogue_stage = 4
            self.dialogue_start_time = current_time

        # Handle fade effect
        if self.fading:
            self.fade_alpha += 5  # Increase opacity
            if self.fade_alpha >= 255:  # Fully black, switch scenes
                self.pookie.has_unlocked_car = True
                if self.dialogue_stage == 4 and current_time - self.dialogue_start_time >= 1500:
                    self.scene_manager.set_scene(Wohnzimmer(self.scene_manager, self.pookie, 55, 206))

    def handle_event(self, event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.letBerduxSay("Glückwunsch, Sie haben ihren Bachelor geschafft!")
                if event.key == pygame.K_ESCAPE:
                    from scenes.wohnzimmer_scene import Wohnzimmer
                    self.scene_manager.set_scene(Wohnzimmer(self.scene_manager, self.pookie, 55, 206))

    def render(self, screen, debug_mode=False):
        screen.blit(self.bg, self.bg_rect)
        if self.gong:
            screen.blit(self.gong, self.gong_rect)

        if hasattr(self, "pookie_message_box"):
            if pygame.time.get_ticks() - self.message_display_time < self.message_duration:
                # Draw the white box
                screen.blit(self.pookie_message_box[0], self.pookie_message_box[1])

                # Draw the character image
                screen.blit(self.pookie_character_image[0], self.pookie_character_image[1])

                # Draw the text lines
                text_surfaces, text_start_pos = self.pookie_message_text
                x, y = text_start_pos
                for text_surface in text_surfaces:
                    screen.blit(text_surface, (x, y))
                    y += text_surface.get_height() + 5

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

        if self.fading:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))
