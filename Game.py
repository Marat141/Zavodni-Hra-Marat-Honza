import pygame
import tkinter as tk
from tkinter import messagebox

# Inicializace pygame
pygame.init()

# Inicializace Tkinter pro dialogová okna
root = tk.Tk()
root.withdraw()  # Skrytí hlavního okna Tkinter

# Získání velikosti obrazovky
info = pygame.display.Info()
WIDTH, HEIGHT = 800, 600  # Výchozí velikost okna
FPS = 60

# Barvy
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
HIGHLIGHT = (150, 150, 150)  # Barva zvýraznění
CLICKED = (200, 200, 200)    # Barva při kliknutí

# Vytvoření okna s možností změny velikosti
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("2D Racing Game")

# Načtení obrázku auta
car_image = pygame.image.load("Racing-car-front.png")
car_width, car_height = 50, 100
car_image = pygame.transform.scale(car_image, (car_width, car_height))
car_x, car_y = WIDTH // 2 - car_width // 2, HEIGHT - car_height - 20
car_direction = "front"

# Rychlost pohybu
speed = 5
fullscreen = False

# Herní stav
in_menu = True

def draw_menu(mouse_pos, clicked_button):
    screen.fill(GRAY)
    font = pygame.font.Font(None, 50)
    title = font.render("Race Game", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    button_font = pygame.font.Font(None, 40)
    buttons = ["Hrát", "Výběr mapy", "Výběr auta", "Nastavení"]
    button_rects = []
    for i, text in enumerate(buttons):
        rect = pygame.Rect(WIDTH // 2 - 100, 150 + i * 80, 200, 50)
        color = WHITE
    
        if rect.collidepoint(mouse_pos):
            color = HIGHLIGHT
        if clicked_button == text:
            color = CLICKED
            
        pygame.draw.rect(screen, color, rect, border_radius=10)
        btn_text = button_font.render(text, True, BLACK)
        screen.blit(btn_text, (rect.centerx - btn_text.get_width() // 2, rect.centery - btn_text.get_height() // 2))
        button_rects.append((rect, text))
    
    return button_rects

# Herní smyčka
running = True
clock = pygame.time.Clock()
mouse_pos = (0, 0)
clicked_button = None

while running:
    clock.tick(FPS)
    
    if in_menu:
        button_rects = draw_menu(mouse_pos, clicked_button)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in button_rects:
                    if rect.collidepoint(event.pos):
                        clicked_button = action  # Uložíme, na které tlačítko bylo kliknuto
            elif event.type == pygame.MOUSEBUTTONUP:
                for rect, action in button_rects:
                    if rect.collidepoint(event.pos) and clicked_button == action:
                        if action == "Hrát":
                            in_menu = False
                        elif action == "Výběr mapy":
                            messagebox.showinfo("Výběr mapy", "Zde si vyberete mapu.")
                        elif action == "Výběr auta":
                            messagebox.showinfo("Výběr auta", "Zde si vyberete auto.")
                        elif action == "Nastavení":
                            messagebox.showinfo("Nastavení", "Zde bude možnost změny jazyka.")
                clicked_button = None  # Reset kliknutého tlačítka po provedení akce

    else:
        # Herní logika
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                        WIDTH, HEIGHT = info.current_w, info.current_h
                    else:
                        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                        WIDTH, HEIGHT = 800, 600
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()
            elif event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        # Ovládání auta
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            car_x -= speed
            car_direction = "left"
        if keys[pygame.K_d]:
            car_x += speed
            car_direction = "right"
        if keys[pygame.K_w]:
            car_y -= speed
            car_direction = "front"
        if keys[pygame.K_s]:
            car_y += speed
            car_direction = "back"

        # Zabránění pohybu mimo obrazovku
        car_x = max(0, min(car_x, WIDTH - car_width))
        car_y = max(0, min(car_y, HEIGHT - car_height))

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
        screen.fill(BLACK)
        screen.blit(rotated_car, (car_x, car_y))
        pygame.display.flip()
    
pygame.quit()