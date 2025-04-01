import pygame
pygame.init()

screen_width, screen_height = 1440, 720
screen = pygame.display.set_mode((screen_width, screen_height))
scaled_image = pygame.transform.scale( pygame.image.load('pic/block.png'), (64, 64))
image_rect = scaled_image.get_rect(center=(screen_width//2, screen_height//2))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(scaled_image, image_rect)
    pygame.display.flip()

pygame.quit()