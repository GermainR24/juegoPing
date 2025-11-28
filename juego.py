import pygame
import math
import random
import os

# --- Inicialización ---
pygame.init()

# --- Constantes ---
ANCHO = 1280
ALTO = 720
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Air Hockey: Legends - In Game")

# Colores
BLANCO = (235, 235, 235)
ROJO = (200, 50, 50)
ROJO_OSCURO = (150, 30, 30)
AZUL = (50, 50, 200)
NEGRO = (0, 0, 0)
GRIS_OSCURO = (100, 100, 100) 

# Colores de Poderes
VERDE = (50, 200, 50)
MORADO = (150, 50, 150)
CYAN = (0, 255, 255)
AMARILLO = (255, 215, 0)

# Configuración de Poderes
PODERES_INFO = {
    'BIG':   {'color': VERDE,  'duracion': 15000, 'target': 'self'},
    'SMALL': {'color': MORADO, 'duracion': 10000, 'target': 'enemy'},
    'GHOST': {'color': (200,200,200), 'duracion': 0, 'target': 'ball'},
    'INVERT':{'color': MORADO, 'duracion': 5000,  'target': 'enemy'},
    'FAST':  {'color': ROJO,   'duracion': 4000,  'target': 'ball'},
    'SLOW':  {'color': AZUL,   'duracion': 3000,  'target': 'ball'},
    'MULTI': {'color': (255,165,0), 'duracion': 8000, 'target': 'game'},
    'SHIELD':{'color': CYAN,   'duracion': 10000, 'target': 'self'},
    'ZIGZAG':{'color': AMARILLO, 'duracion': 5000,  'target': 'ball'}
}
LISTA_PODERES = list(PODERES_INFO.keys())

# Físicas
FRICCION = 0.995
VELOCIDAD_PALETA_BASE = 9


# --- Cargar Imagen (Versión sin protección) ---
def cargar_imagen(nombre, escala=None):
    # Busca en la carpeta assets, si no está, asume que está en la raíz
    ruta = os.path.join("assets", nombre)
    if not os.path.exists(ruta):
        ruta = nombre
    
    # Carga directa. Si la imagen no existe, el programa dará error aquí.
    img = pygame.image.load(ruta).convert_alpha()
    
    if escala:
        img = pygame.transform.scale(img, escala)
        
    return img

img_fondo = cargar_imagen("cancha.jpg", (ANCHO, ALTO))

# --- Clases ---

class PoderItem:
    def __init__(self):
        self.tipo = random.choice(LISTA_PODERES)
        self.x = random.randint(100, ANCHO - 100)
        self.y = random.randint(50, ALTO - 50)
        self.radio = 15
        self.tiempo_creacion = pygame.time.get_ticks()
        self.duracion_en_suelo = 5000 

    def dibujar(self):
        edad = pygame.time.get_ticks() - self.tiempo_creacion
        if edad > 3500 and (edad // 200) % 2 == 0:
            return 

        color = PODERES_INFO[self.tipo]['color']
        pygame.draw.circle(PANTALLA, color, (self.x, self.y), self.radio)
        pygame.draw.circle(PANTALLA, NEGRO, (self.x, self.y), self.radio, 2)
        
        fuente_peq = pygame.font.Font(None, 20)
        texto = fuente_peq.render(self.tipo[:3], True, NEGRO)
        PANTALLA.blit(texto, (self.x - 10, self.y - 5))

class Paleta:
    def __init__(self, x, y, es_izquierda, imagen=None):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.radio_base = 35 # Un poco más grande para que se vean bien las caras
        self.radio = self.radio_base
        self.es_izquierda = es_izquierda
        self.rect = pygame.Rect(x - self.radio, y - self.radio, self.radio * 2, self.radio * 2)
        
        self.inventario = [None, None, None] 
        self.efectos = {} 
        self.tiene_escudo = False

        # --- MANEJO DE IMAGEN ---
        self.imagen_original = imagen
        self.imagen_actual = None
        self.actualizar_imagen() # Crear la imagen del tamaño correcto inicial

    def actualizar_imagen(self):
        """Escala la imagen original al tamaño actual del radio (útil para poderes BIG/SMALL)"""
        if self.imagen_original:
            # Escalamos la imagen al diámetro actual (radio * 2)
            diametro = int(self.radio * 2)
            self.imagen_actual = pygame.transform.scale(self.imagen_original, (diametro, diametro))

    def aplicar_efecto(self, tipo, duracion):
        tiempo_actual = pygame.time.get_ticks()
        self.efectos[tipo] = tiempo_actual + duracion
        
        cambio_tamano = False
        if tipo == 'BIG':
            self.radio = int(self.radio_base * 1.5)
            cambio_tamano = True
        elif tipo == 'SMALL':
            self.radio = int(self.radio_base * 0.7)
            cambio_tamano = True
        elif tipo == 'SHIELD':
            self.tiene_escudo = True
            
        if cambio_tamano:
            self.actualizar_imagen()

    def actualizar_efectos(self):
        tiempo_actual = pygame.time.get_ticks()
        efectos_a_borrar = []
        cambio_tamano = False

        for tipo, tiempo_fin in self.efectos.items():
            if tiempo_actual > tiempo_fin:
                efectos_a_borrar.append(tipo)
        
        for tipo in efectos_a_borrar:
            del self.efectos[tipo]
            if tipo == 'BIG' or tipo == 'SMALL':
                self.radio = self.radio_base
                cambio_tamano = True
            if tipo == 'SHIELD':
                self.tiene_escudo = False
        
        if cambio_tamano:
            self.actualizar_imagen()

    def mover(self, dx, dy):
        if 'INVERT' in self.efectos:
            dx = -dx
            dy = -dy

        self.x += dx
        self.y += dy

        # Límites
        if self.y - self.radio < 0: self.y = self.radio
        if self.y + self.radio > ALTO: self.y = ALTO - self.radio

        if self.es_izquierda:
            if self.x - self.radio < 0: self.x = self.radio
            if self.x + self.radio > ANCHO // 2: self.x = ANCHO // 2 - self.radio
        else:
            if self.x - self.radio < ANCHO // 2: self.x = ANCHO // 2 + self.radio
            if self.x + self.radio > ANCHO: self.x = ANCHO - self.radio

    def dibujar(self):
        # Si tenemos imagen, dibujamos la imagen
        if self.imagen_actual:
            # Centramos la imagen en las coordenadas x, y
            rect_img = self.imagen_actual.get_rect(center=(int(self.x), int(self.y)))
            PANTALLA.blit(self.imagen_actual, rect_img)
            
            # Dibujamos un borde de color para indicar efectos o equipo
            color_borde = ROJO if self.es_izquierda else AZUL
            if 'INVERT' in self.efectos: color_borde = MORADO
            pygame.draw.circle(PANTALLA, color_borde, (int(self.x), int(self.y)), self.radio, 3)

        else:
            # Si NO hay imagen, usamos el círculo rojo clásico
            color = ROJO
            if 'INVERT' in self.efectos: color = MORADO 
            pygame.draw.circle(PANTALLA, color, (int(self.x), int(self.y)), self.radio)
            pygame.draw.circle(PANTALLA, ROJO_OSCURO, (int(self.x), int(self.y)), int(self.radio * 0.8), 3)

        if self.tiene_escudo:
            pos_x_escudo = 30 if self.es_izquierda else ANCHO - 30
            pygame.draw.line(PANTALLA, CYAN, (pos_x_escudo, 0), (pos_x_escudo, ALTO), 5)

class Disco:
    def __init__(self, x=ANCHO//2, y=ALTO//2):
        self.x = x
        self.y = y
        self.radio = 15
        self.vel_x = 0
        self.vel_y = 0
        self.fantasma_rebotes = 0 
        self.es_extra = False
        self.tiempo_creacion = pygame.time.get_ticks()
        self.fin_zigzag = 0

    def aplicar_efecto(self, tipo):
        if tipo == 'FAST':
            self.vel_x *= 1.4
            self.vel_y *= 1.4
        elif tipo == 'SLOW':
            self.vel_x *= 0.6
            self.vel_y *= 0.6
        elif tipo == 'GHOST':
            self.fantasma_rebotes = 3
        elif tipo == 'ZIGZAG':
            self.fin_zigzag = pygame.time.get_ticks() + 1500

    def mover(self, paleta_izq, paleta_der):
        self.x += self.vel_x
        self.y += self.vel_y

        if pygame.time.get_ticks() < self.fin_zigzag:
            oscilacion = math.sin(pygame.time.get_ticks() * 0.01) * 40
            self.y += oscilacion

        rebotado = False
        if self.y - self.radio <= 0:
            self.y = self.radio
            self.vel_y *= -1
            rebotado = True
        elif self.y + self.radio >= ALTO:
            self.y = ALTO - self.radio
            self.vel_y *= -1
            rebotado = True

        zona_gol_top = ALTO // 2 - 110
        zona_gol_bot = ALTO // 2 + 110
        
        if paleta_izq.tiene_escudo and self.x - self.radio < 35 and self.vel_x < 0:
             self.x = 40
             self.vel_x *= -1
             rebotado = True
        
        if paleta_der.tiene_escudo and self.x + self.radio > ANCHO - 35 and self.vel_x > 0:
             self.x = ANCHO - 40
             self.vel_x *= -1
             rebotado = True

        if self.x - self.radio <= 0:
            if self.y < zona_gol_top or self.y > zona_gol_bot:
                self.x = self.radio
                self.vel_x *= -1
                rebotado = True
            else: return "GOL_DERECHA" 

        if self.x + self.radio >= ANCHO:
            if self.y < zona_gol_top or self.y > zona_gol_bot:
                self.x = ANCHO - self.radio
                self.vel_x *= -1
                rebotado = True
            else: return "GOL_IZQUIERDA"

        self.vel_x *= FRICCION
        self.vel_y *= FRICCION

        if rebotado and self.fantasma_rebotes > 0:
            self.fantasma_rebotes -= 1

        if self.es_extra:
            if pygame.time.get_ticks() - self.tiempo_creacion > 8000:
                return "EXPIRADO"
        return None

    def dibujar(self):
        color_bola = AZUL
        if pygame.time.get_ticks() < self.fin_zigzag:
            color_bola = AMARILLO

        if self.fantasma_rebotes > 0:
            pygame.draw.circle(PANTALLA, (200, 200, 255), (int(self.x), int(self.y)), self.radio, 1)
        else:
            pygame.draw.circle(PANTALLA, color_bola, (int(self.x), int(self.y)), self.radio)
            if color_bola == AZUL:
                pygame.draw.circle(PANTALLA, (100, 100, 255), (int(self.x - 5), int(self.y - 5)), 5)
            else:
                pygame.draw.circle(PANTALLA, BLANCO, (int(self.x - 5), int(self.y - 5)), 5)

# --- Funciones Auxiliares ---

def chequear_colision_disco(paleta, disco):
    dx = disco.x - paleta.x
    dy = disco.y - paleta.y
    distancia = math.hypot(dx, dy)

    if distancia < paleta.radio + disco.radio:
        angulo = math.atan2(dy, dx)
        fuerza = 12 
        disco.vel_x = math.cos(angulo) * fuerza
        disco.vel_y = math.sin(angulo) * fuerza
        superposicion = (paleta.radio + disco.radio) - distancia
        disco.x += math.cos(angulo) * superposicion
        disco.y += math.sin(angulo) * superposicion

def dibujar_interfaz(p1, p2, score1, score2):
    PANTALLA.blit(img_fondo, (0, 0))
    
    fuente = pygame.font.Font(None, 74)
    texto_puntaje = fuente.render(f"{score1}   {score2}", True, (240, 240, 240))
    rect_texto = texto_puntaje.get_rect(center=(ANCHO//2, ALTO - 50))
    texto_sombra = fuente.render(f"{score1}   {score2}", True, NEGRO)
    PANTALLA.blit(texto_sombra, (rect_texto.x + 2, rect_texto.y + 2))
    PANTALLA.blit(texto_puntaje, rect_texto)

    fuente_inv = pygame.font.Font(None, 24)
    
    # Inventario P1
    teclas_j1 = ['Q', 'E', 'R']
    y_inv = 20
    for i in range(3):
        tecla = teclas_j1[i]
        poder = p1.inventario[i]
        texto = fuente_inv.render(f"[{tecla}] {poder if poder else '---'}", True, BLANCO if not poder else ROJO)
        s = pygame.Surface((texto.get_width() + 4, texto.get_height() + 4))
        s.set_alpha(100)
        s.fill(NEGRO)
        PANTALLA.blit(s, (18, y_inv - 2))
        PANTALLA.blit(texto, (20, y_inv))
        y_inv += 25
    
    # Inventario P2
    teclas_j2 = ['I', 'O', 'P']
    y_inv = 20
    for i in range(3):
        tecla = teclas_j2[i]
        poder = p2.inventario[i]
        texto = fuente_inv.render(f"[{tecla}] {poder if poder else '---'}", True, BLANCO if not poder else (100, 100, 255))
        ancho_txt = texto.get_width()
        s = pygame.Surface((ancho_txt + 4, texto.get_height() + 4))
        s.set_alpha(100)
        s.fill(NEGRO)
        PANTALLA.blit(s, (ANCHO - 22 - ancho_txt, y_inv - 2))
        PANTALLA.blit(texto, (ANCHO - 20 - ancho_txt, y_inv))
        y_inv += 25

def activar_poder(jugador_origen, jugador_destino, discos_juego, slot_index):
    tipo_poder = jugador_origen.inventario[slot_index]
    if tipo_poder is not None:
        jugador_origen.inventario[slot_index] = None
        info = PODERES_INFO[tipo_poder]
        if info['target'] == 'self':
            jugador_origen.aplicar_efecto(tipo_poder, info['duracion'])
        elif info['target'] == 'enemy':
            jugador_destino.aplicar_efecto(tipo_poder, info['duracion'])
        elif info['target'] == 'ball':
            for d in discos_juego: d.aplicar_efecto(tipo_poder)
        elif info['target'] == 'game':
            if tipo_poder == 'MULTI':
                nuevo_disco = Disco(ANCHO//2, ALTO//2)
                nuevo_disco.vel_x = random.choice([-5, 5])
                nuevo_disco.vel_y = random.choice([-5, 5])
                nuevo_disco.es_extra = True
                discos_juego.append(nuevo_disco)

# --- FUNCIÓN PRINCIPAL MODIFICADA ---
# Ahora acepta los datos de los jugadores seleccionados
def juego(datos_p1=None, datos_p2=None):
    reloj = pygame.time.Clock()
    corriendo = True
    
    # Extraemos las imágenes si existen
    img1 = datos_p1['imagen'] if datos_p1 else None
    img2 = datos_p2['imagen'] if datos_p2 else None

    # Creamos las paletas pasando las imágenes
    j1 = Paleta(100, ALTO // 2, True, img1)
    j2 = Paleta(ANCHO - 100, ALTO // 2, False, img2)
    
    discos = [Disco()] 
    items_suelo = []   
    puntaje1 = 0
    puntaje2 = 0
    ultimo_spawn = pygame.time.get_ticks()
    PROXIMO_SPAWN = random.randint(5000, 10000)

    while corriendo:
        tiempo_actual = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_q: activar_poder(j1, j2, discos, 0)
                if evento.key == pygame.K_e: activar_poder(j1, j2, discos, 1)
                if evento.key == pygame.K_r: activar_poder(j1, j2, discos, 2)
                if evento.key == pygame.K_i: activar_poder(j2, j1, discos, 0)
                if evento.key == pygame.K_o: activar_poder(j2, j1, discos, 1)
                if evento.key == pygame.K_p: activar_poder(j2, j1, discos, 2)

        teclas = pygame.key.get_pressed()
        v1 = VELOCIDAD_PALETA_BASE
        if teclas[pygame.K_w]: j1.mover(0, -v1)
        if teclas[pygame.K_s]: j1.mover(0, v1)
        if teclas[pygame.K_a]: j1.mover(-v1, 0)
        if teclas[pygame.K_d]: j1.mover(v1, 0)

        v2 = VELOCIDAD_PALETA_BASE
        if teclas[pygame.K_UP]: j2.mover(0, -v2)
        if teclas[pygame.K_DOWN]: j2.mover(0, v2)
        if teclas[pygame.K_LEFT]: j2.mover(-v2, 0)
        if teclas[pygame.K_RIGHT]: j2.mover(v2, 0)

        j1.actualizar_efectos()
        j2.actualizar_efectos()

        if tiempo_actual - ultimo_spawn > PROXIMO_SPAWN:
            items_suelo.append(PoderItem())
            ultimo_spawn = tiempo_actual
            PROXIMO_SPAWN = random.randint(5000, 10000)
        items_suelo = [p for p in items_suelo if tiempo_actual - p.tiempo_creacion < p.duracion_en_suelo]

        for item in items_suelo[:]:
            recogido = False
            # --- JUGADOR 1 ---
            if math.hypot(item.x - j1.x, item.y - j1.y) < j1.radio + item.radio:
                # 1. VERIFICACIÓN DE VARIEDAD:
                # Solo intentamos recogerlo si NO lo tenemos ya en el inventario
                if item.tipo not in j1.inventario:
                    for i in range(3):
                        if j1.inventario[i] is None:
                            j1.inventario[i] = item.tipo
                            items_suelo.remove(item)
                            recogido = True
                            break 
            
            # --- JUGADOR 2 ---
            # Solo chequeamos si J1 no se lo llevó primero
            if not recogido and math.hypot(item.x - j2.x, item.y - j2.y) < j2.radio + item.radio:
                # 1. VERIFICACIÓN DE VARIEDAD:
                if item.tipo not in j2.inventario:
                    for i in range(3):
                        if j2.inventario[i] is None:
                            j2.inventario[i] = item.tipo
                            items_suelo.remove(item)
                            break

        discos_a_borrar = []
        for d in discos:
            res = d.mover(j1, j2)
            if res == "GOL_IZQUIERDA":
                if not d.es_extra:
                    puntaje1 += 1
                    d.x, d.y = ANCHO//2, ALTO//2
                    d.vel_x, d.vel_y = 0, 0
                else: discos_a_borrar.append(d)
                pygame.time.delay(100)
            elif res == "GOL_DERECHA":
                if not d.es_extra:
                    puntaje2 += 1
                    d.x, d.y = ANCHO//2, ALTO//2
                    d.vel_x, d.vel_y = 0, 0
                else: discos_a_borrar.append(d)
                pygame.time.delay(100)
            elif res == "EXPIRADO": discos_a_borrar.append(d)
            chequear_colision_disco(j1, d)
            chequear_colision_disco(j2, d)
        for d in discos_a_borrar:
            if d in discos: discos.remove(d)

        dibujar_interfaz(j1, j2, puntaje1, puntaje2)
        for item in items_suelo: item.dibujar()
        j1.dibujar()
        j2.dibujar()
        for d in discos: d.dibujar()

        pygame.display.flip()
        reloj.tick(60)
    
    return

if __name__ == "__main__":
    juego()