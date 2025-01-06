import pygame
from Items import Item
from character.animated_character import AnimatedCharacter
from helper.debug_box import draw_debug_info

class gym:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

        self.original_width, self.original_height = 736, 598  # Originalgröße des Bildes
        self.bg_image = pygame.image.load("assets/backgrounds/pixel_art_gym_room.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg_image, (600, 600))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Pookie
        self.character = AnimatedCharacter(0, 500)  # Start at left edge
        self.character.disable_movement = True
        self.character.current_animation = "walk_right"  # Walk animation

        # Zielposition auf der Matte
        self.target_x = 210  # Beispiel: x-Position der Matte
        self.target_y = 450  # Beispiel: y-Position der Matte

        # Hantel-Status
        self.lifting_weights = False  # Status: Hantel-Animation aktiv
        self.weights_animation_done = False  # Status: Hantel-Animation abgeschlossen


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln
                from scenes.wohnzimmer_scene import Wohnzimmer
                self.scene_manager.set_scene(Wohnzimmer(self.scene_manager))

    def update(self, dt):
         # Bewegung nur ausführen, wenn die Hantel-Animation nicht läuft
        if not self.lifting_weights:
            self.move_character_to_mattress()

        # Hantel-Animation ausführen
        if self.lifting_weights:
            self.lift_weights()

        self.character.update(dt)

    def render(self, screen, debug_mode=False):
        # Rendern der Esszimmer-Szene
        screen.blit(self.bg, self.bg_rect)
        self.character.render(screen)

    def move_character_to_mattress(self):
        # Zielkoordinaten
        target_x = self.target_x
        target_y = self.target_y

        # Charakterposition (Mitte)
        character_center = self.character.rect.center

        # Berechnung der Richtung
        direction_x = target_x - character_center[0]
        direction_y = target_y - character_center[1]

        # Distanz berechnen
        distance = max(abs(direction_x), abs(direction_y))

        if distance > 0:
            # Normalisierung der Richtung
            velocity_x = direction_x / distance
            velocity_y = direction_y / distance

            # Bewegungsgeschwindigkeit
            movement_speed = 2

            # Bewegung aktualisieren
            self.character.rect.x += velocity_x * movement_speed
            self.character.rect.y += velocity_y * movement_speed

            # Animation entsprechend der Richtung setzen
            if abs(direction_x) > abs(direction_y):  # Horizontale Bewegung priorisieren
                if direction_x > 0:
                    self.character.force_animation("walk_right")
                else:
                    self.character.force_animation("walk_left")
            else:  # Vertikale Bewegung
                if direction_y > 0:
                    self.character.force_animation("walk_down")
                else:
                    self.character.force_animation("walk_up")

        # Ziel erreicht: Bewegung stoppen
        if abs(character_center[0] - target_x) < 5 and abs(character_center[1] - target_y) < 5:
            self.character.disable_movement = True
            self.character.force_animation("idle")
            self.lifting_weights = True  # Starte Hantel-Animation
    
    def lift_weights(self):
        if not self.weights_animation_done:  # Animation starten
            self.character.animation_speed = 500  # Verlangsame die Animationsgeschwindigkeit
            self.character.force_animation("hantel")
            print("Startet Hantel-Animation...")
            self.weights_animation_done = True  # Markiere als abgeschlossens 