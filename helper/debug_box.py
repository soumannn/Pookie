import pygame

def draw_debug_info(screen, rect, text, font, color=(255, 255, 255), text_offset=(0, -20), rect_color=None):
    """
    Draws a rectangle and associated debug text on the screen.

    :param screen: Pygame screen surface
    :param rect: Pygame rect (rectangle) to outline
    :param text: Debug text to display
    :param font: Pygame font object for rendering the text
    :param color: Color of the text (default: white)
    :param text_offset: Tuple (x, y) for offsetting the text position (default: above the rect)
    :param rect_color: Color of the rectangle outline (default: same as text color)
    """
    # Draw the rectangle outline
    rect_color = rect_color or color
    pygame.draw.rect(screen, rect_color, rect, 2)

    # Render and draw the text
    text_surface = font.render(text, True, color)
    text_position = (rect.x + text_offset[0], rect.y + text_offset[1])
    screen.blit(text_surface, text_position)
