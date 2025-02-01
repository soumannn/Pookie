import pygame

class Gym:
    def __init__(self, scene_manager, pookie):
        self.scene_manager = scene_manager
        self.pookie = pookie

        self.pookie.calibrate_sensor()

        # Fenstergröße an Wohnzimmer anpassen
        self.window_width, self.window_height = 640, 480  

        # Hintergrund
        self.bg_image = pygame.image.load("assets/backgrounds/gym_background__d4fc0171.png").convert()
        self.bg = pygame.transform.scale(self.bg_image, (self.window_width, self.window_height))
        self.bg_rect = self.bg.get_rect(topleft=(0, 0))

        # Pookie
        self.pookie.character.set_position(100, 300)  # Startposition
        self.pookie.character.disable_movement = True
        self.pookie.character.force_animation("walk_right")  # Startanimation

        # Zielposition auf der Matte
        self.target_x = 390  # Beispiel: x-Position der Matte
        self.target_y = 340  # Beispiel: y-Position der Matte

        # Hantel-Status
        self.lifting_weights = False  # Status: Hantel-Animation aktiv
        self.weights_animation_done = False  # Status: Hantel-Animation abgeschlossen

    def move_character_to_mattress(self):
        """ Pookie läuft von links zur Matte """
        character_center = self.pookie.character.rect.center

        # Pookie soll NUR nach rechts laufen, ohne Y zu verändern
        if character_center[0] < self.target_x:
            self.pookie.character.rect.x += 2  # Bewegung nach rechts
            self.pookie.character.force_animation("walk_right")  # Immer nach rechts laufen
        else:
            self.pookie.character.disable_movement = True
            self.pookie.character.force_animation("idle")
            self.lifting_weights = True  # Starte Hantel-Animation

    def lift_weights(self):
        if not self.weights_animation_done:  # Animation starten
            self.pookie.character.force_animation("hantel")
            print("Startet Hantel-Animation...")
            self.weights_animation_done = True  # Markiere als abgeschlossen


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln

                self.scene_manager.set_scene(self.scene_manager.scenes[0](self.scene_manager, self.pookie))
            if event.key == pygame.K_r:
                self.initialize_state()

    def initialize_state(self):
        """Helper function to initialize scene state."""
        print("trying to reset..")
        self.pookie.character.disable_movement = False

    def update(self, dt):
        self.pookie.check_shake()

         # Bewegung nur ausführen, wenn die Hantel-Animation nicht läuft
        if not self.lifting_weights:
            self.move_character_to_mattress()

        # Hantel-Animation ausführen
        if self.lifting_weights:
            self.lift_weights()

        self.pookie.character.update(dt)

    def render(self, screen, debug_mode=False):
        # Rendern der Gym-Szene
        screen.blit(self.bg, self.bg_rect)
        self.pookie.character.render(screen)