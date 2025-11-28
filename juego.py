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
AMARILLO_ULTI = (255, 215, 0) # Color de la barra de ulti lista

# Colores de Poderes (Items del suelo)
VERDE = (50, 200, 50)
MORADO = (150, 50, 150)
CYAN = (0, 255, 255)

# Configuración de Items del Suelo
PODERES_INFO = {
    'BIG':   {'color': VERDE,  'duracion': 15000, 'target': 'self'},
    'SMALL': {'color': MORADO, 'duracion': 10000, 'target': 'enemy'},
    'GHOST': {'color': (200,200,200), 'duracion': 0, 'target': 'ball'},
    'INVERT':{'color': MORADO, 'duracion': 5000,  'target': 'enemy'},
    'FAST':  {'color': ROJO,   'duracion': 4000,  'target': 'ball'},
    'SLOW':  {'color': AZUL,   'duracion': 3000,  'target': 'ball'},
    'MULTI': {'color': (255,165,0), 'duracion': 8000, 'target': 'game'},
    'SHIELD':{'color': CYAN,   'duracion': 2000, 'target': 'self'},
    'ZIGZAG':{'color': AMARILLO_ULTI, 'duracion': 5000,  'target': 'ball'}
}
LISTA_PODERES = list(PODERES_INFO.keys())

# --- CONFIGURACIÓN DE ULTIMATES (PERSONAJES) ---
# cd = Cooldown en milisegundos (ej: 25000 = 25 segundos)
ULTI_DATA = {
    'M. CURIE': {'cd': 20000, 'duracion': 0,    'tipo': 'FISION'},       # Multibola
    'EINSTEIN': {'cd': 25000, 'duracion': 3000, 'tipo': 'RELATIVIDAD'},  # Slow Motion al enemigo
    'GAUSS':    {'cd': 18000, 'duracion': 0,    'tipo': 'IMAN'},         # Tiro sónico
    'STEVE':    {'cd': 22000, 'duracion': 5000, 'tipo': 'BEDROCK'},      # Muro
    'TESLA':    {'cd': 20000, 'duracion': 0,    'tipo': 'TELEPORT'},     # Teleport bola
}
# Default por si no coincide el nombre
ULTI_DEFAULT = {'cd': 20000, 'duracion': 0, 'tipo': 'NONE'}

# Físicas
FRICCION = 0.995
VELOCIDAD_PALETA_BASE = 9

# --- Cargar Imagen ---
def cargar_imagen(nombre, escala=None):
    # Busca en la carpeta assets, si no está, busca en la raíz
    ruta = os.path.join("assets", nombre)
    if not os.path.exists(ruta):
        ruta = nombre
    # Sin protección try/except para detectar errores de archivos faltantes
    img = pygame.image.load(ruta).convert_alpha()
    if escala:
        img = pygame.transform.scale(img, escala)
    return img

# Intenta cargar png, si no jpg (por si acaso cambiaste la extensión)
try:
    img_fondo = cargar_imagen("cancha.png", (ANCHO, ALTO))
except:
    try:
        img_fondo = cargar_imagen("cancha.jpg", (ANCHO, ALTO))
    except:
        print("Error: No se encontró cancha.png ni cancha.jpg")
        img_fondo = pygame.Surface((ANCHO, ALTO))
        img_fondo.fill((20, 20, 20))

# --- Clases ---

class PoderItem:
    def __init__(self):
        self.tipo = random.choice(LISTA_PODERES)
        self.x = random.randint(100, ANCHO - 100)
        self.y = random.randint(50, ALTO - 50)
        self.radio = 15
        self.tiempo_creacion = pygame.time.get_ticks()
        self.duracion_en_suelo = 6000 

    def dibujar(self):
        edad = pygame.time.get_ticks() - self.tiempo_creacion
        if edad > 4500 and (edad // 200) % 2 == 0:
            return # Parpadeo antes de desaparecer

        color = PODERES_INFO[self.tipo]['color']
        pygame.draw.circle(PANTALLA, color, (self.x, self.y), self.radio)
        pygame.draw.circle(PANTALLA, NEGRO, (self.x, self.y), self.radio, 2)
        
        fuente_peq = pygame.font.Font(None, 20)
        texto = fuente_peq.render(self.tipo[:3], True, NEGRO)
        PANTALLA.blit(texto, (self.x - 10, self.y - 5))

class Paleta:
    def __init__(self, x, y, es_izquierda, nombre_personaje, imagen=None):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.radio_base = 35 
        self.radio = self.radio_base
        self.es_izquierda = es_izquierda
        self.rect = pygame.Rect(x - self.radio, y - self.radio, self.radio * 2, self.radio * 2)
        
        self.inventario = [None, None, None] 
        self.efectos = {} 
        self.tiene_escudo = False

        # --- SISTEMA DE ULTI ---
        self.nombre = nombre_personaje
        self.config_ulti = ULTI_DATA.get(self.nombre, ULTI_DEFAULT)
        
        self.cooldown_max = self.config_ulti['cd']
        self.ultimo_uso_ulti = -self.cooldown_max # Para que empiece lista
        
        self.ulti_activa_hasta = 0 
        self.velocidad_afectada = 1.0 

        # Muro de Steve
        self.muro_rect = None 
        if self.config_ulti['tipo'] == 'BEDROCK':
            distancia_al_arco = 30 
            muro_x = distancia_al_arco if es_izquierda else ANCHO - distancia_al_arco - 20
            self.muro_rect = pygame.Rect(muro_x, ALTO//2 - 100, 20, 200)

        # Manejo de Imagen
        self.imagen_original = imagen
        self.imagen_actual = None
        self.actualizar_imagen()

    def actualizar_imagen(self):
        if self.imagen_original:
            diametro = int(self.radio * 2)
            self.imagen_actual = pygame.transform.scale(self.imagen_original, (diametro, diametro))

    def puede_usar_ulti(self):
        ahora = pygame.time.get_ticks()
        return (ahora - self.ultimo_uso_ulti) >= self.cooldown_max

    def activar_ulti_sistema(self):
        if self.puede_usar_ulti():
            self.ultimo_uso_ulti = pygame.time.get_ticks()
            if self.config_ulti['duracion'] > 0:
                self.ulti_activa_hasta = pygame.time.get_ticks() + self.config_ulti['duracion']
            return True
        return False

    def aplicar_efecto(self, tipo, duracion):
        tiempo_actual = pygame.time.get_ticks()
        self.efectos[tipo] = tiempo_actual + duracion
        
        cambio_tamano = False
        if tipo == 'BIG':
            self.radio = int(self.radio_base * 2)
            cambio_tamano = True
        elif tipo == 'SMALL':
            self.radio = int(self.radio_base * 0.5)
            cambio_tamano = True
        elif tipo == 'SHIELD':
            self.tiene_escudo = True
            
        if cambio_tamano:
            self.actualizar_imagen()

    def actualizar_efectos(self):
        tiempo_actual = pygame.time.get_ticks()
        
        # 1. Limpiar efectos de items
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

        # 2. Resetear velocidad (IMPORTANTE: Esto debe pasar antes de aplicar el freno de Einstein)
        self.velocidad_afectada = 1.0

    def mover(self, dx, dy):
        # Aplicar factor de velocidad
        dx *= self.velocidad_afectada
        dy *= self.velocidad_afectada

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
        if self.imagen_actual:
            rect_img = self.imagen_actual.get_rect(center=(int(self.x), int(self.y)))
            PANTALLA.blit(self.imagen_actual, rect_img)
            color_borde = ROJO if self.es_izquierda else AZUL
            if 'INVERT' in self.efectos: color_borde = MORADO
            pygame.draw.circle(PANTALLA, color_borde, (int(self.x), int(self.y)), self.radio, 3)
        else:
            color = ROJO
            if 'INVERT' in self.efectos: color = MORADO 
            pygame.draw.circle(PANTALLA, color, (int(self.x), int(self.y)), self.radio)
            pygame.draw.circle(PANTALLA, ROJO_OSCURO, (int(self.x), int(self.y)), int(self.radio * 0.8), 3)

        if self.tiene_escudo:
            pos_x_escudo = 30 if self.es_izquierda else ANCHO - 30
            pygame.draw.line(PANTALLA, CYAN, (pos_x_escudo, 0), (pos_x_escudo, ALTO), 5)
        
        if self.config_ulti['tipo'] == 'BEDROCK' and pygame.time.get_ticks() < self.ulti_activa_hasta:
            pygame.draw.rect(PANTALLA, (100, 100, 100), self.muro_rect) 
            pygame.draw.rect(PANTALLA, NEGRO, self.muro_rect, 2) 
            for y_linea in range(self.muro_rect.top, self.muro_rect.bottom, 20):
                pygame.draw.line(PANTALLA, NEGRO, (self.muro_rect.left, y_linea), (self.muro_rect.right, y_linea))

    def dibujar_barra_ulti(self):
        ahora = pygame.time.get_ticks()
        tiempo_pasado = ahora - self.ultimo_uso_ulti
        porcentaje = min(tiempo_pasado / self.cooldown_max, 1.0)
        
        ancho_barra = 80
        alto_barra = 8
        x_barra = self.x - ancho_barra // 2
        y_barra = self.y + self.radio + 10
        
        pygame.draw.rect(PANTALLA, GRIS_OSCURO, (x_barra, y_barra, ancho_barra, alto_barra))
        color_relleno = AMARILLO_ULTI if porcentaje >= 1.0 else (100, 100, 100)
        pygame.draw.rect(PANTALLA, color_relleno, (x_barra, y_barra, int(ancho_barra * porcentaje), alto_barra))
        pygame.draw.rect(PANTALLA, NEGRO, (x_barra, y_barra, ancho_barra, alto_barra), 1)

        if porcentaje >= 1.0:
            f = pygame.font.Font(None, 18)
            tecla_txt = "L-SHIFT" if self.es_izquierda else "R-SHIFT"
            t = f.render(f"ULTI LISTA! [{tecla_txt}]", True, NEGRO)
            PANTALLA.blit(t, (x_barra - 10, y_barra + 10))


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
            self.vel_x *= 1.8
            self.vel_y *= 1.8
        elif tipo == 'SLOW':
            self.vel_x *= 0.4
            self.vel_y *= 0.4
        elif tipo == 'GHOST':
            self.fantasma_rebotes = 3
        elif tipo == 'ZIGZAG':
            self.fin_zigzag = pygame.time.get_ticks() + 1500

    def mover(self, paleta_izq, paleta_der):
        self.x += self.vel_x
        self.y += self.vel_y

        if pygame.time.get_ticks() < self.fin_zigzag:
            oscilacion = math.sin(pygame.time.get_ticks() * 0.01) * 15
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
        
        # Muro Steve P1
        rect_bola = pygame.Rect(self.x - self.radio, self.y - self.radio, self.radio*2, self.radio*2)
        if paleta_izq.config_ulti['tipo'] == 'BEDROCK' and pygame.time.get_ticks() < paleta_izq.ulti_activa_hasta:
             if paleta_izq.muro_rect and rect_bola.colliderect(paleta_izq.muro_rect):
                 self.vel_x = abs(self.vel_x)
                 rebotado = True
        
        # Muro Steve P2
        if paleta_der.config_ulti['tipo'] == 'BEDROCK' and pygame.time.get_ticks() < paleta_der.ulti_activa_hasta:
             if paleta_der.muro_rect and rect_bola.colliderect(paleta_der.muro_rect):
                 self.vel_x = -abs(self.vel_x)
                 rebotado = True

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
            color_bola = AMARILLO_ULTI

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

def activar_poder_item(jugador_origen, jugador_destino, discos_juego, slot_index):
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

def ejecutar_ulti_especial(p_origen, p_enemigo, discos):
    tipo = p_origen.config_ulti['tipo']
    
    if tipo == 'FISION': # M. CURIE
        for _ in range(2):
            d = Disco(p_origen.x, p_origen.y)
            d.vel_x = random.choice([-8, 8])
            d.vel_y = random.choice([-8, 8])
            d.es_extra = True
            discos.append(d)
            
    elif tipo == 'RELATIVIDAD': # EINSTEIN
        p_enemigo.velocidad_afectada = 0.1 # 10% de velocidad (Casi congelado)
        
    elif tipo == 'IMAN': # GAUSS
        bola = discos[0]
        target_x = ANCHO - 20 if p_origen.es_izquierda else 20
        target_y = ALTO // 2
        dx = target_x - bola.x
        dy = target_y - bola.y
        angulo = math.atan2(dy, dx)
        velocidad_sonica = 25
        bola.vel_x = math.cos(angulo) * velocidad_sonica
        bola.vel_y = math.sin(angulo) * velocidad_sonica
        
    elif tipo == 'TELEPORT': # TESLA
        bola = discos[0]
        zona_enemiga_x = ANCHO - 250 if p_origen.es_izquierda else 250
        bola.x = zona_enemiga_x
        bola.y = random.randint(100, ALTO - 100)
        bola.vel_x = 2 if p_origen.es_izquierda else -2
        bola.vel_y = random.choice([-3, 3])

    elif tipo == 'BEDROCK': # STEVE
        pass 

# --- FUNCIÓN PRINCIPAL ---
def juego(datos_p1=None, datos_p2=None):
    reloj = pygame.time.Clock()
    corriendo = True
    
    img1 = datos_p1['imagen'] if datos_p1 else None
    nom1 = datos_p1['nombre'] if datos_p1 else 'JUGADOR 1'
    
    img2 = datos_p2['imagen'] if datos_p2 else None
    nom2 = datos_p2['nombre'] if datos_p2 else 'JUGADOR 2'

    j1 = Paleta(150, ALTO // 2, True, nom1, img1)
    j2 = Paleta(ANCHO - 150, ALTO // 2, False, nom2, img2)
    
    discos = [Disco()] 
    items_suelo = []   
    puntaje1 = 0
    puntaje2 = 0
    ultimo_spawn = pygame.time.get_ticks()
    PROXIMO_SPAWN = random.randint(5000, 10000)

    while corriendo:
        tiempo_actual = pygame.time.get_ticks()

        # 1. EVENTOS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: corriendo = False
            
            if evento.type == pygame.KEYDOWN:
                # Items
                if evento.key == pygame.K_q: activar_poder_item(j1, j2, discos, 0)
                if evento.key == pygame.K_e: activar_poder_item(j1, j2, discos, 1)
                if evento.key == pygame.K_r: activar_poder_item(j1, j2, discos, 2)
                if evento.key == pygame.K_i: activar_poder_item(j2, j1, discos, 0)
                if evento.key == pygame.K_o: activar_poder_item(j2, j1, discos, 1)
                if evento.key == pygame.K_p: activar_poder_item(j2, j1, discos, 2)

                # Ultimates
                if evento.key == pygame.K_LSHIFT:
                    if j1.activar_ulti_sistema():
                        ejecutar_ulti_especial(j1, j2, discos)
                
                if evento.key == pygame.K_RSHIFT:
                    if j2.activar_ulti_sistema():
                        ejecutar_ulti_especial(j2, j1, discos)

        # 2. ACTUALIZAR ESTADOS Y EFECTOS (PRIMERO)
        # Esto resetea velocidad a 1.0
        j1.actualizar_efectos()
        j2.actualizar_efectos()

        # 3. APLICAR ULTI DE EINSTEIN (SEGUNDO)
        # Esto sobrescribe la velocidad si Einstein está activo
        if j1.config_ulti['tipo'] == 'RELATIVIDAD' and tiempo_actual < j1.ulti_activa_hasta:
            j2.velocidad_afectada = 0.1 # 10% Velocidad
        if j2.config_ulti['tipo'] == 'RELATIVIDAD' and tiempo_actual < j2.ulti_activa_hasta:
            j1.velocidad_afectada = 0.1

        # 4. MOVIMIENTO (TERCERO)
        # Ahora se mueven con la velocidad correcta
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

        # 5. LÓGICA DE JUEGO
        if tiempo_actual - ultimo_spawn > PROXIMO_SPAWN:
            items_suelo.append(PoderItem())
            ultimo_spawn = tiempo_actual
            PROXIMO_SPAWN = random.randint(5000, 10000)
        items_suelo = [p for p in items_suelo if tiempo_actual - p.tiempo_creacion < p.duracion_en_suelo]

        for item in items_suelo[:]:
            recogido = False
            # J1
            if math.hypot(item.x - j1.x, item.y - j1.y) < j1.radio + item.radio:
                if item.tipo not in j1.inventario: 
                    for i in range(3):
                        if j1.inventario[i] is None:
                            j1.inventario[i] = item.tipo
                            items_suelo.remove(item)
                            recogido = True
                            break 
            # J2
            if not recogido and math.hypot(item.x - j2.x, item.y - j2.y) < j2.radio + item.radio:
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
                pygame.time.delay(50)
            elif res == "GOL_DERECHA":
                if not d.es_extra:
                    puntaje2 += 1
                    d.x, d.y = ANCHO//2, ALTO//2
                    d.vel_x, d.vel_y = 0, 0
                else: discos_a_borrar.append(d)
                pygame.time.delay(50)
            elif res == "EXPIRADO": discos_a_borrar.append(d)
            chequear_colision_disco(j1, d)
            chequear_colision_disco(j2, d)
        for d in discos_a_borrar:
            if d in discos: discos.remove(d)

        # 6. DIBUJADO
        dibujar_interfaz(j1, j2, puntaje1, puntaje2)
        for item in items_suelo: item.dibujar()
        
        j1.dibujar()
        j1.dibujar_barra_ulti()
        j2.dibujar()
        j2.dibujar_barra_ulti()
        
        for d in discos: d.dibujar()

        pygame.display.flip()
        reloj.tick(60)
    
    return

if __name__ == "__main__":
    juego()