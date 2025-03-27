import pygame

# Inicializace pygame
pygame.init()

# Konstanty
WIDTH, HEIGHT = 800, 600
FPS = 60

# Barvy
BLACK = (0, 0, 0)

# Vytvoření okna
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Racing Game")

# Načtení obrázku auta
car_image = pygame.image.load("Racing-car-front.png")
car_image = pygame.transform.scale(car_image, (50, 100))
car_x, car_y = WIDTH // 2, HEIGHT - 120  # Startovní pozice
car_direction = "front"  # Směr auta

# Rychlost pohybu
speed = 5

# Herní smyčka
running = True
clock = pygame.time.Clock()
while running:
    clock.tick(FPS)
    
    # Zpracování událostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Ovládání auta
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:  # Pohyb doleva
        car_x -= speed
        car_direction = "left"
    elif keys[pygame.K_d]:  # Pohyb doprava
        car_x += speed
        car_direction = "right"
    elif keys[pygame.K_w]:  # Pohyb nahoru
        car_y -= speed
        car_direction = "front"
    elif keys[pygame.K_s]:  # Pohyb dolů
        car_y += speed
        car_direction = "back"
    elif keys[pygame.K_a and pygame.K_w]:
        car_x -= speed
        car_y -= speed
        
    
    # Otočení auta
    if car_direction == "left":
        rotated_car = pygame.transform.rotate(car_image, 90)
    elif car_direction == "right":
        rotated_car = pygame.transform.rotate(car_image, -90)
    elif car_direction == "front":
        rotated_car = pygame.transform.rotate(car_image, 0)
    elif car_direction == "back":
        rotated_car = pygame.transform.rotate(car_image, 180)
    
    # Vykreslení
    screen.fill(BLACK)  # Černé pozadí
    screen.blit(rotated_car, (car_x, car_y))
    pygame.display.flip()
    
pygame.quit()
