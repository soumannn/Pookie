import pygame

class Item:
    def __init__(self, sprite_sheet_path, sprite_width, sprite_height, rows, cols):
        """
        Initializes the Furniture class to extract furniture sprites.

        Args:
        - sprite_sheet_path: Path to the sprite sheet image.
        - sprite_width: Width of each individual sprite.
        - sprite_height: Height of each individual sprite.
        - rows: Number of rows in the sprite sheet.
        - cols: Number of columns in the sprite sheet.
        """
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.sprites = []

        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        print("Sprite sheet dimensions:", self.sprite_sheet.get_width(), self.sprite_sheet.get_height())

        # Extract individual sprites
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height

                # Check if the rectangle is within bounds
                if x + sprite_width <= self.sprite_sheet.get_width() and y + sprite_height <= self.sprite_sheet.get_height():
                    sprite = self.sprite_sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height))
                    self.sprites.append(sprite)
                else:
                    print(f"Skipping out-of-bounds sprite at row {row}, col {col}")

    def __getitem__(self, index):
        """
        Allows indexing like item[1].
        """
        return self.sprites[index]

    def __len__(self):
        """
        Returns the number of sprites.
        """
        return len(self.sprites)