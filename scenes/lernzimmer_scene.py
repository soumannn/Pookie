import pygame, requests
from Items import Item
from character.animated_character import AnimatedCharacter


class Lernzimmer:
    def __init__(self, scene_manager, pookie, detector=None):
        self.scene_manager = scene_manager
        self.pookie = pookie

        #self.pookie.startDetectionThread()
        if self.pookie.onRaspi:
            self.pookie.calibrate_sensor()

        # Debug font
        self.debug_font = pygame.font.Font(None, 24)

        # Background
        self.bg_sprites = Item("assets/spritesheets/floorwall.png", 64, 112, 1, 5)
        self.bg = pygame.transform.scale(self.bg_sprites[2], (640, 480))
        self.cozy_bg = self.pookie.apply_cozy_solo(self.bg.copy())
        self.bg_rect = self.cozy_bg.get_rect(topleft=(0, 0))

        # Table
        self.table_image = pygame.image.load("assets/models/table.png").convert_alpha()
        self.table_image = pygame.transform.scale(self.table_image, (268, 170))
        self.cozy_table = self.pookie.apply_cozy_solo(self.table_image.copy())
        self.table_rect = self.cozy_table.get_rect(topleft=(310, 400))

        # Chair
        self.chair_image = pygame.image.load("assets/models/chair.png").convert_alpha()
        self.chair_image = pygame.transform.scale(self.chair_image, (100, 140))
        self.cozy_chair = self.pookie.apply_cozy_solo(self.chair_image.copy())
        self.chair_rect = self.cozy_chair.get_rect(topleft=(395, 300))

        # Carpet 
        self.carpet_image = pygame.image.load("assets/models/carpet.png").convert_alpha()
        self.carpet_image = pygame.transform.scale(self.carpet_image, (312, 208))
        self.cozy_carpet = self.pookie.apply_cozy_solo(self.carpet_image.copy())
        self.carpet_rect = self.cozy_carpet.get_rect(topleft=(288, 342))

        # Big Bookshelf 
        self.bookshelf_b_image = pygame.image.load("assets/models/bookshelf_big.png").convert_alpha()
        self.bookshelf_b_image = pygame.transform.scale(self.bookshelf_b_image, (276, 282))
        self.cozy_bookshelf_b = self.pookie.apply_cozy_solo(self.bookshelf_b_image.copy())
        self.bookshelf_b_rect = self.cozy_bookshelf_b.get_rect(topleft=(5, 30))

        # Tablelamp
        self.table_lamp_sprites = Item("assets/spritesheets/tablelamps.png", 15, 23, 1, 2)
        self.table_lamp = pygame.transform.scale(self.table_lamp_sprites[1], (60, 92))
        self.cozy_tablelamp = self.pookie.apply_cozy_solo(self.table_lamp.copy())
        self.table_lamp_rect = self.cozy_tablelamp.get_rect(topleft=(510, 400))

        # Music Player
        self.music_player_image = pygame.image.load("assets/models/music_player.png").convert_alpha()
        self.music_player_image = pygame.transform.scale(self.music_player_image, (150, 100))
        self.cozy_music_player = self.pookie.apply_cozy_solo(self.music_player_image.copy())
        self.music_player_rect = self.cozy_music_player.get_rect(topleft=(273, 200))
        
        # Small Bookshelf
        self.bookshelf_s_image = pygame.image.load("assets/models/bookshelf_small.png").convert_alpha()
        self.bookshelf_s_image = pygame.transform.scale(self.bookshelf_s_image, (150, 100))
        self.cozy_bookshelf_s = self.pookie.apply_cozy_solo(self.bookshelf_s_image.copy())
        self.bookshelf_s_rect = self.cozy_bookshelf_s.get_rect(topleft=(425, 200))

        # Fish Tank
        self.fish_tank_image = pygame.image.load("assets/models/fish_tank.png").convert_alpha()
        self.fish_tank_image = pygame.transform.scale(self.fish_tank_image, (60, 60))
        self.cozy_fish_tank = self.pookie.apply_cozy_solo(self.fish_tank_image.copy())
        self.fish_tank_rect = self.cozy_fish_tank.get_rect(topleft=(465, 160))

        # Tree Pot
        self.tree_pot_image = pygame.image.load("assets/models/tree_pot.png").convert_alpha()
        self.tree_pot_image = pygame.transform.scale(self.tree_pot_image, (70, 150))
        self.cozy_tree_pot = self.pookie.apply_cozy_solo(self.tree_pot_image.copy())
        self.tree_pot_rect = self.cozy_tree_pot.get_rect(topleft=(20, 300))

        # Wall Shelf
        self.wall_shelf_image = pygame.image.load("assets/models/wall_shelf.png").convert_alpha()
        self.wall_shelf_image = pygame.transform.scale(self.wall_shelf_image, (150, 50))
        self.cozy_wall_shelf = self.pookie.apply_cozy_solo(self.wall_shelf_image.copy())
        self.wall_shelf_rect = self.cozy_wall_shelf.get_rect(topleft=(400, 60))

        # Small Pot 1
        self.small_pot_1_image = pygame.image.load("assets/models/small_pot_1.png").convert_alpha()
        self.small_pot_1_image = pygame.transform.scale(self.small_pot_1_image, (50, 50))
        self.cozy_small_pot_1 = self.pookie.apply_cozy_solo(self.small_pot_1_image.copy())
        self.small_pot_1_rect = self.cozy_small_pot_1.get_rect(topleft=(430, 40))

        # Small Pot 2
        self.small_pot_2_image = pygame.image.load("assets/models/small_pot_2.png").convert_alpha()
        self.small_pot_2_image = pygame.transform.scale(self.small_pot_2_image, (40, 40))
        self.cozy_small_pot_2 = self.pookie.apply_cozy_solo(self.small_pot_2_image.copy())
        self.small_pot_2_rect = self.cozy_small_pot_2.get_rect(topleft=(480, 60))

        # Character setup
        #self.character = AnimatedCharacter(0, 346)
        self.pookie.character.disable_movement = True
        self.pookie.character.current_animation = "walk_right"
        self.pookie.character.rect.x = 0
        self.is_walking = True  # Start walking to chair

        self.is_leaving = False 
        self.using_handy = False


    def print_click_position(self, event):
        """Print the position of a mouse click to the terminal."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at position: {event.pos}")

    def setUsingHandy(self, bool):
        self.using_handy = bool

    def initialize_state(self):
        """Helper function to initialize scene state."""
        print("trying to reset..")
        self.pookie.character.disable_movement = False

    def handle_walk_to_chair(self):
        target_x = self.chair_rect.centerx - 10
        target_y = self.chair_rect.centery - 35
        character_center = self.pookie.character.rect.center

        # Calculate direction
        direction_x = target_x - character_center[0]
        direction_y = target_y - character_center[1]

        # Normalize direction
        distance = max(abs(direction_x), abs(direction_y))
        if distance > 0:
            self.pookie.character.velocity.x = direction_x / distance
            self.pookie.character.velocity.y = direction_y / distance

        # Move character
        movement_speed = 2  # Speed for walking to the target
        self.pookie.character.rect.x += self.pookie.character.velocity.x * movement_speed
        self.pookie.character.rect.y += self.pookie.character.velocity.y * movement_speed

        # Check if the character reached the target position
        if abs(character_center[0] - target_x) < 5 and abs(character_center[1] - target_y) < 5:
            self.is_walking = False  # Stop walking
            self.pookie.character.current_animation = "buch_lesen"

    def handle_left_learn_room(self):
        self.pookie.character.disable_movement = True
        self.pookie.character.force_animation("walk_left")

        movement_speed = 2
        self.pookie.character.rect.x -= movement_speed

        if self.pookie.character.rect.right < 0:
            self.scene_manager.set_scene(self.scene_manager.scenes[0](self.scene_manager, self.pookie, 618,278))

    def handle_use_handy(self):
        self.is_walking = False
        self.pookie.character.disable_movement = True
        self.pookie.walk_to_animation = "handy_modus"

        #self.walk_to = True
        self.pookie.walk_to = True

        self.pookie.walk_to_target = (448, 303)  # Target position for TikTok mode (244, 190)
        # self.pookie.handy += 1
        # print(f'{self.pookie.learn} {self.pookie.handy}')
        self.pookie.letPookieSay(self.pookie.tikTokMessage())

    def update(self, dt):
        self.pookie.check_shake()

        if self.is_walking:
            self.handle_walk_to_chair()
        
        if self.is_leaving:
            self.handle_left_learn_room()

        if self.pookie.walk_to_livingroom:
            self.pookie.handle_walk_to_livingroom(left=True)

        if self.using_handy:
            self.handle_left_learn_room()
            self.handle_use_handy()

        # Update the character animation
        self.pookie.character.update(dt)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Zum Wohnzimmer zurückwechseln
                self.is_leaving = True  # Start leaving the room
            elif event.key == pygame.K_t:
                # self.pookie.handy += 1
                self.using_handy = True
            elif event.key == pygame.K_r:
                self.initialize_state()
            elif event.key == pygame.K_a:
                self.pookie.triggerAutoEvent()

    def render(self, screen, debug_mode=False):
        screen.blit(self.cozy_bg, self.bg_rect)
        screen.blit(self.cozy_bookshelf_b, self.bookshelf_b_rect)
        screen.blit(self.cozy_bookshelf_s, self.bookshelf_s_rect)
        screen.blit(self.cozy_music_player, self.music_player_rect)
        screen.blit(self.cozy_fish_tank, self.fish_tank_rect)
        #screen.blit(self.cozy_tree_pot, self.tree_pot_rect)
        screen.blit(self.cozy_wall_shelf, self.wall_shelf_rect)
        screen.blit(self.cozy_small_pot_1, self.small_pot_1_rect)
        screen.blit(self.cozy_small_pot_2, self.small_pot_2_rect)
        screen.blit(self.cozy_carpet, self.carpet_rect)
        screen.blit(self.cozy_chair, self.chair_rect)
        #screen.blit(self.cozy_table, self.table_rect)

        objects = [
            (self.cozy_tree_pot, self.tree_pot_rect),
            (self.cozy_table, self.table_rect),
            (self.pookie.character, self.pookie.character.rect,)
        ]

        # Sort objects by their bottom position
        objects.sort(key=lambda obj: obj[1].bottom)

        # Render in the correct order
        for obj, rect in objects:
            if isinstance(obj, type(self.pookie.character)):  # Ensure character uses its render method
                obj.render(screen)
            else:
                screen.blit(obj, rect)

        #self.pookie.character.render(screen)
        screen.blit(self.cozy_tablelamp, self.table_lamp_rect)


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
            else:
                # Remove the message after the duration
                del self.pookie.pookie_message_box
                del self.pookie.pookie_message_text
                del self.pookie.pookie_character_image