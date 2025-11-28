import pygame
import sys
import os
import juego
# --- Inicialización ---
pygame.init()

# --- Configuración de Pantalla ---
ANCHO = 1280
ALTO = 720
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Selección de Equipo - Legends Hockey")

# --- Colores ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL_UI = (50, 100, 150)
VERDE_BOTON = (154, 205, 50)
AZUL_BOTON = (70, 130, 180)
AMARILLO_TEXTO = (255, 215, 0)
GRIS_OSCURO = (50, 50, 50)

# --- Fuentes ---
try:
    FUENTE_TITULO = pygame.font.SysFont("impact", 80)
    FUENTE_NOMBRE = pygame.font.SysFont("impact", 40) # Fuente para nombres de personajes
    FUENTE_BOTON = pygame.font.SysFont("arial", 30, bold=True)
    FUENTE_UI = pygame.font.SysFont("arial", 20)
except:
    FUENTE_TITULO = pygame.font.Font(None, 80)
    FUENTE_NOMBRE = pygame.font.Font(None, 50)
    FUENTE_BOTON = pygame.font.Font(None, 40)
    FUENTE_UI = pygame.font.Font(None, 25)

# --- Función para Cargar Imágenes ---
def cargar_imagen(nombre, escala=None):
    # Busca en la carpeta assets, si no está, busca en la carpeta principal
    ruta = os.path.join("assets", nombre)
    if not os.path.exists(ruta):
        ruta = nombre 
    
    # Carga directa sin "try/except". 
    # Si la imagen no existe, el programa se detendrá aquí y te dirá cuál falta.
    img = pygame.image.load(ruta).convert_alpha()
    
    if escala:
        img = pygame.transform.scale(img, escala)
        
    return img

# --- Cargar Assets Específicos del Usuario ---

# 1. Fondo
img_fondo = cargar_imagen("cancha.jpg", (ANCHO, ALTO))

# 2. UI Genérica (Si no tienes estas, el juego usará cuadros grises)
img_vs = cargar_imagen("vs_logo.png", (150, 150))
img_flecha_izq = cargar_imagen("flecha_izq.png", (50, 50))
img_flecha_der = cargar_imagen("flecha_der.png", (50, 50))

# 3. Datos de los Personajes
# Estructura: {"archivo": nombre_archivo, "nombre": nombre_mostrar, "img": objeto_pygame}
datos_personajes = [
    {"archivo": "curie.png", "nombre": "M. CURIE"},
    {"archivo": "einstein.png", "nombre": "EINSTEIN"},
    {"archivo": "gauss.png", "nombre": "GAUSS"},
    {"archivo": "steve.png", "nombre": "STEVE"}, # Asumo Steve Jobs o Minecraft?
    {"archivo": "tesla.png", "nombre": "TESLA"}
]

# Cargar las imágenes de los personajes en la lista
lista_personajes = []
for p in datos_personajes:
    img = cargar_imagen(p["archivo"], (250, 300)) # Ajusté un poco el tamaño
    lista_personajes.append({
        "nombre": p["nombre"],
        "imagen": img
    })

# --- Estado del Juego ---
# Índices para saber qué personaje ha seleccionado cada jugador
idx_p1 = 0 
idx_p2 = 1 # Empieza con uno diferente al P1

# --- Clases ---

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_base, funcion=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = (min(color_base[0]+30, 255), min(color_base[1]+30, 255), min(color_base[2]+30, 255))
        self.funcion = funcion

    def dibujar(self, superficie):
        pos_mouse = pygame.mouse.get_pos()
        color = self.color_hover if self.rect.collidepoint(pos_mouse) else self.color_base
        pygame.draw.rect(superficie, color, self.rect, border_radius=10)
        pygame.draw.rect(superficie, BLANCO, self.rect, 2, border_radius=10)
        render_texto = FUENTE_BOTON.render(self.texto, True, BLANCO)
        rect_texto = render_texto.get_rect(center=self.rect.center)
        superficie.blit(render_texto, rect_texto)

    def click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.funcion: self.funcion()

class FlechaSelector:
    """ Clase invisible o visible para manejar los clicks en las flechas """
    def __init__(self, x, y, imagen, direccion, jugador_target):
        self.imagen = imagen
        self.rect = self.imagen.get_rect(topleft=(x, y))
        self.direccion = direccion # -1 (izquierda) o 1 (derecha)
        self.jugador_target = jugador_target # 1 o 2

    def dibujar(self, superficie):
        superficie.blit(self.imagen, self.rect)

    def click(self, evento):
        global idx_p1, idx_p2
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.jugador_target == 1:
                    # Lógica cíclica: (actual + dirección) % total
                    idx_p1 = (idx_p1 + self.direccion) % len(lista_personajes)
                else:
                    idx_p2 = (idx_p2 + self.direccion) % len(lista_personajes)

# --- Configuración de Selectores (Flechas) ---
# Definimos posiciones
pos_flecha_izq_p1 = (120, 200)
pos_flecha_der_p1 = (380, 200)
pos_flecha_izq_p2 = (ANCHO - 430, 200)
pos_flecha_der_p2 = (ANCHO - 170, 200)

flechas = [
    FlechaSelector(pos_flecha_izq_p1[0], pos_flecha_izq_p1[1], img_flecha_izq, -1, 1),
    FlechaSelector(pos_flecha_der_p1[0], pos_flecha_der_p1[1], img_flecha_der, 1, 1),
    FlechaSelector(pos_flecha_izq_p2[0], pos_flecha_izq_p2[1], img_flecha_izq, -1, 2),
    FlechaSelector(pos_flecha_der_p2[0], pos_flecha_der_p2[1], img_flecha_der, 1, 2)
]

# --- Loop Principal ---

def salir_juego():
    pygame.quit()
    sys.exit()

def iniciar_juego():
    # 1. Obtenemos el diccionario COMPLETO (que tiene 'nombre' y 'imagen')
    # No pongas ['nombre'] al final, porque necesitamos la imagen también.
    seleccion_p1 = lista_personajes[idx_p1] 
    seleccion_p2 = lista_personajes[idx_p2]
    
    print(f"Juego iniciado: {seleccion_p1['nombre']} vs {seleccion_p2['nombre']}")

    # 2. Se lo enviamos a la función del juego
    juego.juego(seleccion_p1, seleccion_p2)

    # 3. Al volver del juego, restauramos la ventana del menú
    pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Selección de Equipo - Legends Hockey")

boton_back = Boton(50, ALTO - 80, 200, 60, "SALIR", AZUL_BOTON, salir_juego)
boton_play = Boton(ANCHO - 250, ALTO - 80, 200, 60, "JUGAR", VERDE_BOTON, iniciar_juego)

reloj = pygame.time.Clock()

def dibujar_info_seleccion(x_centro, y, indice):
    personaje = lista_personajes[indice]
    
    # 1. Dibujar Nombre entre las flechas
    texto = FUENTE_NOMBRE.render(personaje["nombre"], True, BLANCO)
    rect_texto = texto.get_rect(center=(x_centro, y + 25))
    
    # Sombra del texto
    texto_sombra = FUENTE_NOMBRE.render(personaje["nombre"], True, NEGRO)
    rect_sombra = texto_sombra.get_rect(center=(x_centro + 2, y + 27))
    
    PANTALLA.blit(texto_sombra, rect_sombra)
    PANTALLA.blit(texto, rect_texto)

    # 2. Dibujar Imagen del Personaje debajo
    # Centramos la imagen respecto al centro horizontal dado
    rect_img = personaje["imagen"].get_rect(center=(x_centro, y + 200))
    
    # Un pequeño borde o sombra detrás del personaje para que resalte del fondo
    pygame.draw.rect(PANTALLA, (0,0,0, 100), rect_img.inflate(10, 10), border_radius=15)
    PANTALLA.blit(personaje["imagen"], rect_img)


def dibujar_panel_controles():
    # Fondo del panel
    rect_panel = pygame.Rect(ANCHO//2 - 250, ALTO - 180, 500, 150)
    s = pygame.Surface((500, 150))
    s.set_alpha(220) 
    s.fill((20, 30, 40))
    PANTALLA.blit(s, rect_panel)
    pygame.draw.rect(PANTALLA, AZUL_UI, rect_panel, 3) 

    # Título Panel
    titulo = FUENTE_UI.render("- CONTROLES -", True, AMARILLO_TEXTO)
    PANTALLA.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO - 170))

    # P1
    lbl_p1 = FUENTE_UI.render("JUGADOR 1", True, AZUL_BOTON)
    txt_p1 = FUENTE_UI.render("W A S D \n Q E R", True, BLANCO)
    PANTALLA.blit(lbl_p1, (rect_panel.x + 40, rect_panel.y + 50))
    PANTALLA.blit(txt_p1, (rect_panel.x + 40, rect_panel.y + 80))

    # P2
    lbl_p2 = FUENTE_UI.render("JUGADOR 2", True, (200, 100, 100)) # Rojo suave
    txt_p2 = FUENTE_UI.render("→ ↑ ↓ ← \n U O P", True, BLANCO)
    PANTALLA.blit(lbl_p2, (rect_panel.x + 320, rect_panel.y + 50))
    PANTALLA.blit(txt_p2, (rect_panel.x + 320, rect_panel.y + 80))
    
    # Línea vertical
    pygame.draw.line(PANTALLA, GRIS_OSCURO, (ANCHO//2, ALTO - 140), (ANCHO//2, ALTO - 40), 2)


# --- Loop Principal ---

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            salir_juego()
        
        # --- NUEVO: Selección por Teclado ---
        if evento.type == pygame.KEYDOWN:
            
            # Controles Jugador 1 (Izquierda) -> Teclas A y D
            if evento.key == pygame.K_a: # Mover a la izquierda
                idx_p1 = (idx_p1 - 1) % len(lista_personajes)
            elif evento.key == pygame.K_d: # Mover a la derecha
                idx_p1 = (idx_p1 + 1) % len(lista_personajes)

            # Controles Jugador 2 (Derecha) -> Flechas Teclado
            if evento.key == pygame.K_LEFT: # Mover a la izquierda
                idx_p2 = (idx_p2 - 1) % len(lista_personajes)
            elif evento.key == pygame.K_RIGHT: # Mover a la derecha
                idx_p2 = (idx_p2 + 1) % len(lista_personajes)

        # Manejo de clicks en botones (Play / Salir)
        boton_back.click(evento)
        boton_play.click(evento)
        
        # (Opcional) Si quieres que también funcionen los clicks en las flechas de pantalla:
        for flecha in flechas:
            flecha.click(evento)

    # --- DIBUJADO (Igual que antes) ---
    
    # 1. Dibujar Fondo
    PANTALLA.blit(img_fondo, (0, 0))

    # 2. Título
    texto_titulo = FUENTE_TITULO.render("SELECT TEAM", True, AMARILLO_TEXTO)
    PANTALLA.blit(texto_titulo, (ANCHO//2 - texto_titulo.get_width()//2, 30))

    # 3. Logo VS
    rect_vs = img_vs.get_rect(center=(ANCHO//2, 300))
    PANTALLA.blit(img_vs, rect_vs)

    # 4. Dibujar Flechas visuales
    for flecha in flechas:
        flecha.dibujar(PANTALLA)

    # 5. Dibujar Selección Actualizada
    # Como modificamos idx_p1 y idx_p2 con el teclado, esto se actualiza solo:
    dibujar_info_seleccion(275, 200, idx_p1)       # P1
    dibujar_info_seleccion(ANCHO - 275, 200, idx_p2) # P2

    # 6. Panel y Botones UI
    dibujar_panel_controles()
    boton_back.dibujar(PANTALLA)
    boton_play.dibujar(PANTALLA)

    pygame.display.flip()
    reloj.tick(60)