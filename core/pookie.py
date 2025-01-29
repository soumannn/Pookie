import time

from character.animated_character import AnimatedCharacter
from scenes.lernzimmer_scene import Lernzimmer
from scenes.wohnzimmer_scene import Wohnzimmer
import pygame
import textwrap
import numpy as np
import cv2

try:
    from mpu6050 import mpu6050
    import smbus
    print("mpu und smbus erfolgreich importiert")
    import camera
    from threading import Thread
    IS_RASPBERRY_PI = True
except ImportError as e:
    IS_RASPBERRY_PI = False
    print(f"ImportError occurred: {e}")

class Pookie:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.character = AnimatedCharacter(373, 549)
        self.handy = 0
        self.learn = 0
        self.sport = 0
        self.eat = 0
        self.walk_to = False
        self.walk_to_animation = ""
        self.walk_to_target = None
        self.message_font = pygame.font.SysFont('system-ui', 40)
        self.walk_to_learnroom = False
        self.walk_to_livingroom = False

        # Gyrosensor setup (only on Raspberry Pi)
        if IS_RASPBERRY_PI:
            self.sensor = mpu6050(0x68, bus=3)
            #self.calibrate_sensor()
            self.object_detector = camera.ObjectDetector(self.scene_manager, self)

            self.detection_thread = Thread(target=self.object_detector.detect_objects)
            self.detection_thread.start()
        else:
            self.sensor = None
            self.object_detector = None

    def perform_animation(self, animation_name: str, target: tuple, message: str=""):
        """
        Perform an animation for the character.
        :param animation_name: The name of the animation to perform.
        :param target: The target position (x, y) for the character to walk to.
        """
        print(f"Performing animation '{animation_name}' to target {target}")
        if len(message) > 0:
            self.letPookieSay(message)
        self.walk_to_animation = animation_name
        self.walk_to_target = target
        self.walk_to = True
        self.character.disable_movement = True

    def move_character_towards(self, target_x, target_y, movement_speed=2):
        """
        Helper function to move the character towards a target position.
        """
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
        self.character.rect.x += self.character.velocity.x * movement_speed
        self.character.rect.y += self.character.velocity.y * movement_speed

        # Check if the character reached the target position
        reached_x = abs(character_center[0] - target_x) < 5
        reached_y = abs(character_center[1] - target_y) < 5
        return reached_x and reached_y

    def handle_walk_to_learnroom(self):
        """Handle walking to the learn room at a fixed target position."""
        self.character.disable_movement = True
        self.character.force_animation("walk_right")
        self.letPookieSay(self.bookMessage(), 2000)

        # Hardcoded target position for the learn room
        target_x, target_y = 640, 300

        # Use helper method to move the character
        if self.move_character_towards(target_x, target_y):
            self.walk_to = False  # Stop walking
            self.walk_to_learnroom = False
            self.scene_manager.set_scene(Lernzimmer(self.scene_manager, self))

    def handle_walk_to_livingroom(self, left: bool):
        if left:
            self.character.disable_movement = True
            self.character.force_animation("walk_left")
            target_x, target_y = 0, 300

            if self.move_character_towards(target_x, target_y):
                self.walk_to = False
                self.walk_to_livingroom = False
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager, self))


    def handle_walk_to(self):
        """Handle walking to the target position on the scene."""
        if self.walk_to_target:
            target_x, target_y = self.walk_to_target

            # Use helper method to move the character
            if self.move_character_towards(target_x, target_y):
                self.walk_to = False  # Stop walking
                self.character.force_animation(self.walk_to_animation)


    def letPookieSay(self, message: str, duration: int = 5000):
        """Display a white box with the provided message and the character image on the left side."""
        # Create the white box
        box_width = 640
        box_height = 130
        box_x = (640 - box_width) // 2  # Center the box horizontally
        box_y = 480 - box_height  # Position the box 10px above the bottom of the screen

        white_box = pygame.Surface((box_width, box_height))
        white_box.fill((255, 255, 255))  # Fill the box with white color

        # Wrap the text to fit within the box width
        wrapped_text = textwrap.wrap(message, width=30)  # Adjust width as needed
        text_surfaces = []
        for line in wrapped_text:
            text_surface = self.message_font.render(line, True, (0, 0, 0))  # Black text
            text_surfaces.append(text_surface)

        # Load and scale the character image
        character_image = pygame.image.load("assets/characters/Head.png").convert_alpha()
        character_image = pygame.transform.scale(character_image, (150, 200))  # Scale the character image
        character_rect = character_image.get_rect(
            topleft=(box_x - 40, box_y - 60))  # Position in the left side of the box

        # Save the elements for rendering
        self.pookie_message_box = (white_box, (box_x , box_y))
        self.pookie_message_text = (text_surfaces, (box_x + 140, box_y + 20))  # Adjusted text position
        self.pookie_character_image = (character_image, character_rect)

        # Set a timer to hide the message after a few seconds
        self.message_display_time = pygame.time.get_ticks()
        self.message_duration = duration  # Show message for 5 seconds

    def apply_cozy_effect(self, surface):
        # Convert Pygame surface to NumPy array
        img_array = pygame.surfarray.array3d(surface)
        height, width, _ = img_array.shape

        # Convert to HSV for better color manipulation
        img_hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

        # Adjust Hue towards warmer tones (shift reds/yellows slightly)
        img_hsv[..., 0] = (img_hsv[..., 0] + 5) % 180  # Small hue shift
        img_hsv[..., 1] = cv2.add(img_hsv[..., 1], -20)  # Reduce saturation for softness
        img_hsv[..., 2] = cv2.add(img_hsv[..., 2], 5)  # Slight brightness increase

        # Convert back to RGB
        warm_toned = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)

        # Apply a soft glow effect (blur + brightening)
        blurred = cv2.GaussianBlur(warm_toned, (7, 7), 2)
        soft_glow = cv2.addWeighted(warm_toned, 0.8, blurred, 0.5, 0)

        # Create a vignette effect (darken edges)
        y, x = np.ogrid[:height, :width]
        center_x, center_y = width / 2, height / 2
        vignette = ((x - center_x) ** 2 + (y - center_y) ** 2) / (max(width, height) ** 2)
        vignette = 1 - np.clip(vignette * 2, 0, 1)  # Adjust spread factor
        vignetted = (soft_glow * vignette[..., np.newaxis]).astype(np.uint8)

        # Add a slight film grain (random noise)
        noise = np.random.normal(0, 10, (height, width, 3)).astype(np.uint8)
        grainy = cv2.addWeighted(vignetted, 0.97, noise, 0.03, 0)  # Subtle noise

        # Enhance brightness in highlights for a "bloom" effect
        bright_mask = cv2.inRange(cv2.cvtColor(grainy, cv2.COLOR_RGB2GRAY), 180, 255)
        bright_areas = cv2.GaussianBlur(cv2.cvtColor(bright_mask, cv2.COLOR_GRAY2RGB), (9, 9), 4)
        final_image = cv2.addWeighted(grainy, 0.85, bright_areas, 0.15, 0)

        # Convert back to Pygame surface
        return pygame.surfarray.make_surface(final_image)


    def tikTokMessage(self) -> str:
        if self.handy <= 2:
            return "Let's see what the world is doing today."
        elif 3 <= self.handy <= 5:
            return "Hmm, the world seems a bit weird today..."
        elif 6 <= self.handy <= 8:
            return "Oh no, everything is starting to look cursed..."
        elif 9 <= self.handy <= 12:
            return "Why is everything so chaotic? My brain hurts..."
        elif self.handy > 12:
            return "I can't take it anymore! The brainrot is consuming me!!!"

    def bookMessage(self) -> str:
        if self.handy < self.learn:
            if self.learn <= 2:
                return "Zeit zu lernen ^-^"
            elif self.learn <= 3:
                return "Wusstest du? a² + b² = c², das ist der Satz des Pythagoras!"
            elif self.learn <= 4:
                return "Die Gravitation ist nicht nur, was Äpfel fallen lässt – sie formt das Universum!"
            elif self.learn <= 5:
                return "Wissen ist Macht, aber Weisheit ist die Kunst, es richtig einzusetzen."
            elif self.learn > 6:
                return "ρ(∂v/∂t + v·∇v) = −∇p + μ∇²v + f. Versuch das mal zu lösen!"
            else:
                return "Bücher sind die besten Freunde"
        elif self.handy > self.learn:
            if self.handy <= 2:
                return "Lernen? Ich wäre lieber influencer"
            elif self.handy <= 3:
                return "Ey, wozu brauch ich Mathe, wenn mein Handy alles rechnen kann, lol."
            elif self.handy <= 5:
                return "Was für Schätzer? Guck lieber die neuen TikToks, die sind killer!"
            elif self.handy <= 6:
                return "E = mc-was? Ey, Hauptsache mein Insta-Bild ballert, weißt du."
            else:
                return "Ey, chill mal. Lernen stresst nur, ich bleib bei Netflix und Snacks, bro!"

        return "Lernen.... so langweilig"

