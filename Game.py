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
cars = [
    {"name": "Porsche 911 GT3 RS", "image": "Racing-car-front.png", "rychlost": 320, "akcelerace": 3.2, "ovladatelnost": 9},
    {"name": "BMW M3 GT4", "image": "Racing-car-left.png", "rychlost": 290, "akcelerace": 4.0, "ovladatelnost": 8},
    {"name": "Lamborghini Huracan STO", "image": "Racing-car-Right.png", "rychlost": 330, "akcelerace": 2.9, "ovladatelnost": 8}
]

vybrane_auto_index = 0
in_car_selection = False


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
    
    total_height = len(buttons) * 80
    start_y = HEIGHT // 2 - total_height // 2

    for i, text in enumerate(buttons):
        rect = pygame.Rect(WIDTH // 2 - 100, start_y + i * 80, 200, 50)

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

def vykresli_vyber_auta():
    screen.fill(GRAY)
    font = pygame.font.Font(None, 40)
    nadpis = font.render("Vyber si auto", True, WHITE)
    screen.blit(nadpis, (WIDTH // 2 - nadpis.get_width() // 2, 50))


    auto = cars[vybrane_auto_index]
    try:
        image = pygame.image.load(auto["image"])
        image = pygame.transform.scale(image, (150, 100))
        screen.blit(image, (WIDTH // 2 - 75, 150))
    except:
        pass  # Pokud chybí obrázek, neudělá nic

    jmeno = font.render(auto["name"], True, WHITE)
    screen.blit(jmeno, (WIDTH // 2 - jmeno.get_width() // 2, 270))
    # Vykreslení parametrů auta
    parametry = f"Rychlost: {auto['rychlost']} km/h | Akcelerace: {auto['akcelerace']}s | Ovládatelnost: {auto['ovladatelnost']}/10"
    param_text = font.render(parametry, True, WHITE)
    screen.blit(param_text, (WIDTH // 2 - param_text.get_width() // 2, 310))


    pygame.draw.polygon(screen, WHITE, [(100, 200), (130, 180), (130, 220)])  # ← šipka
    pygame.draw.polygon(screen, WHITE, [(700, 200), (670, 180), (670, 220)])  # → šipka

    pygame.draw.rect(screen, HIGHLIGHT, (WIDTH // 2 - 100, 350, 200, 50), border_radius=10)
    text = font.render("Vybrat", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 360))

def toggle_fullscreen():
    global fullscreen, screen, WIDTH, HEIGHT
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        WIDTH, HEIGHT = info.current_w, info.current_h
    else:
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        WIDTH, HEIGHT = 800, 600



# Herní smyčka
running = True
clock = pygame.time.Clock()
mouse_pos = (0, 0)
clicked_button = None

while running:
    clock.tick(FPS)
    WIDTH, HEIGHT = screen.get_size()
    
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
                            in_menu = False
                            in_car_selection = True
                        elif action == "Nastavení":
                            messagebox.showinfo("Nastavení", "Zde bude možnost změny jazyka.")
                clicked_button = None  # Reset kliknutého tlačítka po provedení akce
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()

    #Logika pro výběr auta
    elif in_car_selection:
        vykresli_vyber_auta()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Kliknutí na levou šipku
                if 100 <= x <= 130 and 180 <= y <= 220:
                    vybrane_auto_index = (vybrane_auto_index - 1) % len(cars)
                # Kliknutí na pravou šipku
                elif 670 <= x <= 700 and 180 <= y <= 220:
                    vybrane_auto_index = (vybrane_auto_index + 1) % len(cars)
                # Kliknutí na tlačítko Vybrat
                elif WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and 350 <= y <= 400:
                    nove_auto = pygame.image.load(cars[vybrane_auto_index]["image"])
                    car_image = pygame.transform.scale(nove_auto, (car_width, car_height))
                    in_car_selection = False
                    in_menu = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()


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