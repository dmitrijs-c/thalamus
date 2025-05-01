import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Brightness Control")

# Define initial values
brightness = 1.0  # Start with 100% brightness
brightness_step = 0.1  # Step size for brightness change

# Set up fonts for rendering text
font = pygame.font.SysFont('arial', 30)  # You can change the font and size as needed

# Function to update the screen with the current brightness
def update_screen(brightness):
    # Create an image (a surface) filled with the current brightness
    color_value = int(255 * brightness)  # Scale brightness to 0-255
    screen.fill((color_value, color_value, color_value))  # Fill the screen with the brightness color
    
    # Render the brightness text
    brightness_text = font.render('Brightness: {}%'.format(int(brightness * 100)), True, (255, 255, 255))
    
    # Calculate the position to center the text at the top middle of the screen
    text_rect = brightness_text.get_rect(center=(screen.get_width() // 2, 30))  # 30px from the top
    
    # Draw the text on the screen
    screen.blit(brightness_text, text_rect)
    
    # Update the display
    pygame.display.update()

# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            # Close the program if the 'Esc' key or the close button is pressed
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # Up arrow increases brightness
                if brightness < 1.0:
                    brightness += brightness_step
                    if brightness > 1.0:
                        brightness = 1.0
            elif event.key == pygame.K_DOWN:  # Down arrow decreases brightness
                if brightness > 0.0:
                    brightness -= brightness_step
                    if brightness < 0.0:
                        brightness = 0.0

    # Update the screen with the current brightness level
    update_screen(brightness)

# Quit pygame
pygame.quit()
sys.exit()
