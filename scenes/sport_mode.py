import pygame

class SportModeScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.message_font = pygame.font.Font(None, 40)
        self.message = self.message_font.render("Sport Mode!", True, (255, 255, 255))

        # Create the character in the middle of the screen
        from character.animated_character import AnimatedCharacter
        self.character = AnimatedCharacter(300, 300)
        self.character.disable_movement = True  # Disable movement
        self.character.current_animation = "pushup"  # Play push-up animation

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Return to the main scene
                from scenes.main_scene import MainScene
                self.scene_manager.set_scene(MainScene(self.scene_manager))

    def update(self, dt):
        # Only update the animation (no movement)
        self.character.update(dt)

    def render(self, screen):
        screen.fill((0, 0, 0))  # Black background
        screen.blit(self.message, (200, 100))
        self.character.render(screen)
