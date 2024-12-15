import pygame
from time import time

class InputHandler:
    def __init__(self):
        self.last_click_time = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_time = time()
            if current_time - self.last_click_time < 0.3:
                print("Double click detected!")
            self.last_click_time = current_time
