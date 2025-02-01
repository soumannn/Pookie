import pygame
from Items import Item
from character.animated_character import AnimatedCharacter
from helper.debug_box import draw_debug_info
import time

class Gym:
    def __init__(self, scene_manager, pookie):
        self.scene_manager = scene_manager
        self.pookie = pookie
        self.pookie.character.disable_movement = False

        # Fenstergröße an Wohnzimmer anpassen
        self.window_width, self.window_height = 640, 480  

        # Hintergrund
        self.bg_image = pygame.image.load("assets/backgrounds/gymm.jpg").convert_alpha()
        self.bg = pygame.transform.scale(self.bg_image, (self.window_width, self.window_height))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Pookie
        self.pookie.character.set_position(100, 300)  # Startposition
        self.pookie.character.disable_movement = True
        self.pookie.character.force_animation("walk_right")  # Startanimation

       
        # Zustand
        self.walking = True
        self.using_weights = False
        self.using_phone = False
        
        self.movement_resume_timer = 0
        self.resume_movement_delay = 500  # 500ms Verzögerung
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zurück ins Wohnzimmer
                from scenes.wohnzimmer_scene import Wohnzimmer
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager, self.pookie))
            elif event.key == pygame.K_h:
                self.start_lifting_weights()
            elif event.key == pygame.K_t:
                self.start_tiktok_mode()

    def update(self, dt):
        if self.walking:
             self.walk_around()
        
        if not self.walking and self.movement_resume_timer > 0:
            self.movement_resume_timer -= dt
            if self.movement_resume_timer <= 0:
                self.movement_resume_timer = 0
                self.pookie.character.disable_movement = False
                self.walking = True

        self.pookie.character.update(dt)

    def render(self, screen, debug_mode=False):
        screen.blit(self.bg, self.bg_rect)
        self.pookie.character.render(screen)

    def start_lifting_weights(self):
        self.pookie.character.disable_movement = True
        self.pookie.character.force_animation("hantel")
        self.using_weights = True
        self.walking = False
        print("Pookie trainiert mit Hanteln!")

    def start_tiktok_mode(self):
        self.pookie.character.disable_movement = True
        self.pookie.character.force_animation("handy_modus")
        self.using_phone = True
        self.walking = False
        print("Pookie schaut TikTok...")

    def walk_around(self):
        """ Pookie läuft zufällig im Gym herum """
        self.pookie.character.disable_movement = False
        speed = 0.02  # Super langsame Bewegung

        if self.pookie.character.force_animation == "walk_right":
            self.pookie.character.rect.x += speed
            if self.pookie.character.rect.x > self.window_width - 50:
                self.pookie.character.force_animation("walk_left")
        else:
            self.pookie.character.rect.x -= speed
            if self.pookie.character.rect.x < 50:
                self.pookie.character.force_animation("walk_right")
