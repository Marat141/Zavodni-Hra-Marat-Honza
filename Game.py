import pygame
import tkinter as tk
from tkinter import messagebox 
import time

# Inicializace knihoven
pygame.init()

# Inicializace Tkinter bez hlavního okna (pro dialogy)
root = tk.Tk()
root.withdraw()

# Informace o velikosti obrazovky
info = pygame.display.Info()
WIDTH, HEIGHT = 800, 600
FPS = 60

# Barvy v RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
HIGHLIGHT = (150, 150, 150)
CLICKED = (200, 200, 200)

# Vytvoření herního okna
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("2D Racing Game")

# Načtení a úprava obrázku auta
car_image = pygame.image.load("Racing-car-front.png")
car_width, car_height = 40, 50
car_image = pygame.transform.scale(car_image, (car_width, car_height))
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 20
car_direction = "front"

cars = [
    {"name": "Porsche 911 GT3 RS", "image": "Porse-front.png", "rychlost": 320, "akcelerace": 3.2, "ovladatelnost": 9},
    {"name": "BMW M3 GT4", "image": "Racing-car-front.png", "rychlost": 290, "akcelerace": 4.0, "ovladatelnost": 8}, #Nenašel jsem obrázek
    {"name": "Lamborghini Huracan STO", "image": "Racing-car-front.png", "rychlost": 330, "akcelerace": 2.9, "ovladatelnost": 8} #Nenašel jsem obrázek
]

vybrane_auto_index = 0
in_car_selection = False
#Vybraná mapa, Seznam map a jejich nastavení
maps = [
    {
        "name": "Ain-Diab-circuit",
        "image": "maps/Ain-Diab-circuit-Asi.png",
        "start_x": 180,
        "start_y": 450,
        "start_dir": "right",
    },
    {
        "name": "Antire Motor racing circuit", 
        "image": "maps/Antire Motor racing circuit - asi.png",
        "start_x": 450,
        "start_y": 500,
        "start_dir": "left"
    },
    {
        "name": "Autodromo Internazionale Enzo e Dino Ferrari",
        "image": "maps/Autodromo Internazionale Enzo e Dino Ferrari.png",
        "start_x": 150,
        "start_y": 480,
        "start_dir": "right"

    },
    {
        "name": "Circuit Dijon-Prenois", 
        "image": "maps/Circuit Dijon-Prenois.png",
        "start_x": 350,
        "start_y": 120,
        "start_dir": "right"

    },
    {
        "name": "Red Bull Ring", 
        "image": "maps/Redbull Ring.png",
        "start_x": 420,
        "start_y": 500,
        "start_dir": "left"

    },
    {
        "name": "Valenica street circuit", 
        "image": "maps/Valenica street circuit.png",
        "start_x": 220,
        "start_y": 310,
    }
]
vybrana_mapa_index = 0
background_image = pygame.image.load(maps[0]["image"])
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
in_map_selection = False

lap_started = False
lap_ready = False

laps = 0
max_laps = 3
lap_times = []
lap_start_time = None
finished = False

start_direction = maps[vybrana_mapa_index].get("start_dir", "front")  # Výchozí směr auta na mapě

fullscreen = False
speed = 5  # výchozí
was_on_finish_line = False

arrow_offset = 200
arrow_y = 200

in_menu = True

def start_position(map_data, width, height): #Tato funkce určuje výchozí pozici auta na mapě a map_data je slovník s informacemi o mapě a width, height jsou šířka a výška okna
    scale_x = width / 800
    scale_y = height / 600
    return int(map_data["start_x"] * scale_x), int(map_data["start_y"] * scale_y)

def is_finish_line(x, y): #Tato funkce určuje, zda je auto na cílové čáře. x, y jsou souřadnice auta
    try:
        pixel_color = background_image.get_at((int(x + car_width / 2), int(y + car_height / 2)))
    except IndexError:
        return False

    return pixel_color[:3] == (0, 0, 0)  # čistá černá

def resize_background():
    global background_image
    mapa = maps[vybrana_mapa_index]
    background_image = pygame.image.load(mapa["image"])
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

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

def toggle_fullscreen():
    global fullscreen, screen, WIDTH, HEIGHT, car_x, car_y, speed
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        WIDTH, HEIGHT = info.current_w, info.current_h
        speed = 15
    else:
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        WIDTH, HEIGHT = 800, 600
        speed = 5
    resize_background()
    car_x, car_y = start_position(maps[vybrana_mapa_index], WIDTH, HEIGHT)


def is_road_color(color, tolerance=15):#Tolerance je tolerance pro detekci šedé barvy
    r, g, b, *_ = color

    # Detekce šedé
    is_gray = abs(r - g) < tolerance and abs(g - b) < tolerance and abs(r - 128) < tolerance

    is_white = r > 240 and g > 240 and b > 240

    is_black = r < 20 and g < 20 and b < 20

    
    is_red = abs(r - 255) < 10 and g < 50 and b < 50

    if is_red:
        return False

    return is_gray or is_white or is_black

def check_off_road(x, y):#
    try:
        pixel_color = background_image.get_at((int(x + car_width / 2), int(y + car_height / 2)))
    except IndexError:
        return True 

    if is_road_color(pixel_color):
        return False 
    return True 

def map_selection():
    global arrow_offset, arrow_y

    # Dynamické přizpůsobení pozice šipek dle velikosti okna
    arrow_offset = WIDTH // 4
    arrow_y = HEIGHT // 2 - 50

    screen.fill(GRAY)
    font = pygame.font.Font(None, 40)
    nadpis = font.render("Vyber si mapu", True, WHITE)
    screen.blit(nadpis, (WIDTH // 2 - nadpis.get_width() // 2, 50))

    mapa = maps[vybrana_mapa_index]
    image = pygame.image.load(mapa["image"])
    image = pygame.transform.scale(image, (300, 200))
    screen.blit(image, (WIDTH // 2 - 150, 100))

    nazev = font.render(mapa["name"], True, WHITE)
    screen.blit(nazev, (WIDTH // 2 - nazev.get_width() // 2, 320))

    # Levá šipka (←)
    pygame.draw.polygon(
        screen, WHITE,
        [(WIDTH // 2 - arrow_offset - 30, arrow_y),
         (WIDTH // 2 - arrow_offset, arrow_y - 20),
         (WIDTH // 2 - arrow_offset, arrow_y + 20)]
    )

    # Pravá šipka (→)
    pygame.draw.polygon(
        screen, WHITE,
        [(WIDTH // 2 + arrow_offset + 30, arrow_y),
         (WIDTH // 2 + arrow_offset, arrow_y - 20),
         (WIDTH // 2 + arrow_offset, arrow_y + 20)]
    )

    # Tlačítko "Vybrat"
    pygame.draw.rect(screen, HIGHLIGHT, (WIDTH // 2 - 100, 370, 200, 50), border_radius=10)
    text = font.render("Vybrat", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 380))

def car_selection():
    global arrow_offset, arrow_y
    arrow_offset = WIDTH // 4
    arrow_y = HEIGHT // 2 - 30

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
        pass

    jmeno = font.render(auto["name"], True, WHITE)
    screen.blit(jmeno, (WIDTH // 2 - jmeno.get_width() // 2, 270))

    # Parametry auta
    parametry = f"Rychlost: {auto['rychlost']} km/h | Akcelerace: {auto['akcelerace']}s | Ovládatelnost: {auto['ovladatelnost']}/10"
    param_text = font.render(parametry, True, WHITE)
    screen.blit(param_text, (WIDTH // 2 - param_text.get_width() // 2, 310))

    # Levá šipka (←)
    pygame.draw.polygon(
        screen, WHITE,
        [(WIDTH // 2 - arrow_offset - 30, arrow_y),
         (WIDTH // 2 - arrow_offset, arrow_y - 20),
         (WIDTH // 2 - arrow_offset, arrow_y + 20)]
    )

    # Pravá šipka (→)
    pygame.draw.polygon(
        screen, WHITE,
        [(WIDTH // 2 + arrow_offset + 30, arrow_y),
         (WIDTH // 2 + arrow_offset, arrow_y - 20),
         (WIDTH // 2 + arrow_offset, arrow_y + 20)]
    )

    # Tlačítko Vybrat
    pygame.draw.rect(screen, HIGHLIGHT, (WIDTH // 2 - 100, 350, 200, 50), border_radius=10)
    text = font.render("Vybrat", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 360))

def show_ingame_message(lines, button_text="OK"):
    waiting = True
    font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 30)
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    
    button_rect = pygame.Rect(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 40)
    
    while waiting:
        screen.blit(overlay, (0, 0))

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, HEIGHT//2 - 60 + i*40))
        
        pygame.draw.rect(screen, HIGHLIGHT, button_rect, border_radius=10)
        button_text_surface = button_font.render(button_text, True, BLACK)
        screen.blit(button_text_surface, (button_rect.centerx - button_text_surface.get_width()//2,
                                          button_rect.centery - button_text_surface.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                waiting = False
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                waiting = False


def ask_ingame_yesno(question_lines):
    waiting = True
    font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 30)
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))

    yes_rect = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 40, 120, 40)
    no_rect = pygame.Rect(WIDTH//2 + 40, HEIGHT//2 + 40, 120, 40)

    while waiting:
        screen.blit(overlay, (0, 0))

        for i, line in enumerate(question_lines):
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, HEIGHT//2 - 60 + i*40))
        
        # YES button
        pygame.draw.rect(screen, HIGHLIGHT, yes_rect, border_radius=10)
        yes_text = button_font.render("Ano", True, BLACK)
        screen.blit(yes_text, (yes_rect.centerx - yes_text.get_width()//2,
                               yes_rect.centery - yes_text.get_height()//2))
        
        # NO button
        pygame.draw.rect(screen, HIGHLIGHT, no_rect, border_radius=10)
        no_text = button_font.render("Ne", True, BLACK)
        screen.blit(no_text, (no_rect.centerx - no_text.get_width()//2,
                              no_rect.centery - no_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event.pos):
                    return True
                elif no_rect.collidepoint(event.pos):
                    return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False


# Herní smyčka
running = True
clock = pygame.time.Clock()
mouse_pos = (0, 0)
clicked_button = None

while running:
    clock.tick(FPS)
    WIDTH, HEIGHT = screen.get_size()# tento řádek kodu dělá to že se velikost okna přizpůsobí velikosti obrazovky
    
    if in_menu:
        button_rects = draw_menu(mouse_pos, clicked_button)
        pygame.display.flip()# tento řádek kodu dělá to že se okno překreslí
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos # tento řádek kodu dělá to že se myš pohybuje po obrazovce
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in button_rects:
                    if rect.collidepoint(event.pos):
                        clicked_button = action 
            elif event.type == pygame.MOUSEBUTTONUP:
                for rect, action in button_rects:
                    if rect.collidepoint(event.pos) and clicked_button == action:
                        if action == "Hrát":
                            in_menu = False
                        elif action == "Výběr mapy":
                            in_menu = False
                            in_map_selection = True
                        elif action == "Výběr auta":
                            in_menu = False
                            in_car_selection = True
                        elif action == "Nastavení":
                            messagebox.showinfo("Nastavení", "Zde bude možnost změny jazyka.") # Ale zatím nic
                clicked_button = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()
    # Logika pro výběr mapy
    elif in_map_selection:
        map_selection()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Kliknutí na levou šipku
                if WIDTH // 2 - arrow_offset - 30 <= x <= WIDTH // 2 - arrow_offset and arrow_y - 20 <= y <= arrow_y + 20:
                    vybrana_mapa_index = (vybrana_mapa_index - 1) % len(maps)
                # Kliknutí na pravou šipku
                elif WIDTH // 2 + arrow_offset <= x <= WIDTH // 2 + arrow_offset + 30 and arrow_y - 20 <= y <= arrow_y + 20:
                    vybrana_mapa_index = (vybrana_mapa_index + 1) % len(maps)
                # Kliknutí na tlačítko Vybrat
                elif WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and 370 <= y <= 420:
                    background_image = pygame.image.load(maps[vybrana_mapa_index]["image"])
                    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
                    # Nastavení výchozí pozice a směru auta
                    car_x, car_y = start_position(maps[vybrana_mapa_index], WIDTH, HEIGHT)
                    car_direction = maps[vybrana_mapa_index].get("start_dir", "front")

                    laps = 0
                    lap_start_time = None# to
                    finished = False# je zde potreb
                    was_on_finish_line = False# 
                    lap_times = []
                    in_map_selection = False
                    in_menu = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()
    #Část kódu pro výběr auta
    elif in_car_selection:
        car_selection()
        pygame.display.flip()# 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Levá šipka
                if WIDTH // 2 - arrow_offset - 30 <= x <= WIDTH // 2 - arrow_offset and arrow_y - 20 <= y <= arrow_y + 20:
                    vybrane_auto_index = (vybrane_auto_index - 1) % len(cars)
                # Pravá šipka
                elif WIDTH // 2 + arrow_offset <= x <= WIDTH // 2 + arrow_offset + 30 and arrow_y - 20 <= y <= arrow_y + 20:
                    vybrane_auto_index = (vybrane_auto_index + 1) % len(cars)
                # Tlačítko Vybrat
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
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit svou hru?"):
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
                    resize_background()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()

        # Ovládání auta
        keys = pygame.key.get_pressed()
        new_x, new_y = car_x, car_y

        if keys[pygame.K_a]:
            test_x = car_x - speed
            if not check_off_road(test_x, car_y):
                new_x = test_x
                car_direction = "left"

        if keys[pygame.K_d]:
            test_x = car_x + speed
            if not check_off_road(test_x, car_y):
                new_x = test_x
                car_direction = "right"

        if keys[pygame.K_w]:
            test_y = car_y - speed
            if not check_off_road(car_x, test_y):
                new_y = test_y
                car_direction = "front"

        if keys[pygame.K_s]:
            test_y = car_y + speed
            if not check_off_road(car_x, test_y):
                new_y = test_y
                car_direction = "back"

        car_x, car_y = new_x, new_y
        center_x = car_x + car_width // 2
        center_y = car_y + car_height // 2

        on_finish_line = is_finish_line(new_x, new_y)

        if on_finish_line and not was_on_finish_line:
            if not lap_start_time:
                lap_start_time = time.time()
            else:
                laps += 1
                if laps >= max_laps:
                    total_time = time.time() - lap_start_time
                    show_ingame_message([f"Dojel jsi {max_laps} kol", f"za {total_time:.2f} sekund!"])
                    finished = True
        was_on_finish_line = on_finish_line

        if laps >= max_laps:
            total_time = time.time() - lap_start_time
            lap_times.append(total_time)
            show_ingame_message([f"Dojel jsi {max_laps} kol", f"za {total_time:.2f} sekund!"])

            again = ask_ingame_yesno(["Chceš jet další kolo?"])
            
            if again:
                laps = 0
                lap_start_time = time.time()

                car_x, car_y = start_position(maps[vybrana_mapa_index], WIDTH, HEIGHT)

                car_direction = "front"
                finished = False
            else:
                draw_menu(mouse_pos, clicked_button)
                in_menu = True


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
        screen.blit(background_image, (0, 0))
        screen.blit(rotated_car, (car_x, car_y)) 
        pygame.display.flip()

        if finished: 
            continue
    
pygame.quit()