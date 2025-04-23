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
car_width, car_height = 25, 50
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

# Nové globální proměnné:
lap_started = False
lap_ready = False

start_direction = maps[vybrana_mapa_index].get("start_dir", "front")  # Výchozí směr auta na mapě

# Rychlost pohybu
speed = 5
fullscreen = False
was_on_finish_line = False


# Herní stav
in_menu = True
# Kontrola jednoho bodu – jestli je na čáře
def is_on_finish_line(x, y):
    try:
        color = background_image.get_at((int(x), int(y)))[:3]
        return color == (0, 0, 0)
    except IndexError:
        return False

# Kontrola více bodů – jestli aspoň jeden z nich je na čáře
def is_on_finish_line_area(x, y, width, height, num_points=3):
    for i in range(num_points):
        point_x = int(x + i * width / (num_points - 1))
        point_y = int(y + height)
        if is_on_finish_line(point_x, point_y):
            return True
    return False

def get_scaled_start_position(map_data, width, height):
    scale_x = width / 800
    scale_y = height / 600
    return int(map_data["start_x"] * scale_x), int(map_data["start_y"] * scale_y)


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
        pass

    jmeno = font.render(auto["name"], True, WHITE)
    screen.blit(jmeno, (WIDTH // 2 - jmeno.get_width() // 2, 270))
    # Vykreslení parametrů auta
    parametry = f"Rychlost: {auto['rychlost']} km/h | Akcelerace: {auto['akcelerace']}s | Ovládatelnost: {auto['ovladatelnost']}/10"
    param_text = font.render(parametry, True, WHITE)
    screen.blit(param_text, (WIDTH // 2 - param_text.get_width() // 2, 310))

    pygame.draw.polygon(screen, WHITE, [(100, 200), (130, 180), (130, 220)])
    pygame.draw.polygon(screen, WHITE, [(700, 200), (670, 180), (670, 220)])

    pygame.draw.rect(screen, HIGHLIGHT, (WIDTH // 2 - 100, 350, 200, 50), border_radius=10)
    text = font.render("Vybrat", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 360))

def toggle_fullscreen():
    global fullscreen, screen, WIDTH, HEIGHT, car_x, car_y
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        WIDTH, HEIGHT = info.current_w, info.current_h
    else:
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        WIDTH, HEIGHT = 800, 600

    resize_background()  # Už tam máš
    car_x, car_y = get_scaled_start_position(maps[vybrana_mapa_index], WIDTH, HEIGHT)


def is_road_color(color, tolerance=15):
    r, g, b, *_ = color

    # Detekce šedé
    is_gray = abs(r - g) < tolerance and abs(g - b) < tolerance and abs(r - 128) < tolerance

    is_white = r > 240 and g > 240 and b > 240

    is_black = r < 20 and g < 20 and b < 20

    
    is_red = abs(r - 255) < 10 and g < 50 and b < 50

    if is_red:
        return False

    return is_gray or is_white or is_black

def check_off_road(x, y):
    try:
        pixel_color = background_image.get_at((int(x + car_width / 2), int(y + car_height / 2)))
    except IndexError:
        return True 

    if is_road_color(pixel_color):
        return False 
    return True 

def vykresli_vyber_mapy():
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

    pygame.draw.polygon(screen, WHITE, [(100, 200), (130, 180), (130, 220)])  # ← šipka
    pygame.draw.polygon(screen, WHITE, [(700, 200), (670, 180), (670, 220)])  # → šipka

    pygame.draw.rect(screen, HIGHLIGHT, (WIDTH // 2 - 100, 370, 200, 50), border_radius=10)
    text = font.render("Vybrat", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 380))

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
                            in_menu = False
                            in_map_selection = True
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
    elif in_map_selection:
        vykresli_vyber_mapy()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if messagebox.askyesno("Ukončení", "Opravdu chcete ukončit hru?"):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Kliknutí na levou šipku
                if 100 <= x <= 130 and 180 <= y <= 220:
                    vybrana_mapa_index = (vybrana_mapa_index - 1) % len(maps)
                # Kliknutí na pravou šipku
                elif 670 <= x <= 700 and 180 <= y <= 220:
                    vybrana_mapa_index = (vybrana_mapa_index + 1) % len(maps)
                # Kliknutí na tlačítko Vybrat
                elif WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and 370 <= y <= 420:
                    background_image = pygame.image.load(maps[vybrana_mapa_index]["image"])
                    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

                    # Nastav pozici auta podle mapy
                    car_x, car_y = get_scaled_start_position(maps[vybrana_mapa_index], WIDTH, HEIGHT)
                    car_direction = maps[vybrana_mapa_index].get("start_dir", "front")

                    in_map_selection = False
                    in_menu = True
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
                    resize_background()  # <<< Tohle je nové

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    pygame.display.iconify()


        # Ovládání auta
        keys = pygame.key.get_pressed()
        # Navrhovaný nový pohyb
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
        # Zabránění pohybu mimo obrazovku
        # Získání středu auta
        center_x = car_x + car_width // 2
        center_y = car_y + car_height // 2

        # Kontrola průjezdu cílové čárou
        if is_on_finish_line_area(car_x, car_y, car_width, car_height):
            if not lap_started:
                lap_started = True
                lap_ready = True
            elif lap_ready and car_direction == start_direction:
                pygame.event.set_blocked(None)
                pygame.event.pump()
                result = messagebox.askquestion(
                    "Cíl!", "Dorazil jste do cíle!\nChcete si dát ještě jedno kolo nebo chcete zpátky do menu?"
                )
                pygame.event.set_allowed(None)
                root.withdraw()

                if result == 'yes':  # Restart kola
                    mapa = maps[vybrana_mapa_index]
                    # Calculate scaled position based on the current screen size
                    car_x, car_y = get_scaled_start_position(mapa, WIDTH, HEIGHT)
                    car_direction = mapa.get("start_dir", "front")
                else:
                    in_menu = True

                lap_started = False
                lap_ready = False
        else:
            if lap_started:
                lap_ready = True


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
        screen.blit(background_image, (0, 0))  # NEJDŘÍV mapa!
        screen.blit(rotated_car, (car_x, car_y))  # Pak auto
        pygame.display.flip()

    
pygame.quit()