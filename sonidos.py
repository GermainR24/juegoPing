import pygame
import os

class GestorSonidos:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.sonidos = {}
        
        self.lista_archivos = {
            # --- Generales ---
            'rebote': 'hit.wav',
            'gol': 'goal.wav',
            'item': 'powerup.wav',
            'click': 'click.wav',
            'musica_menu': 'menu.mp3',
            'musica_juego': 'game.mp3',
            
            # --- Ulti Genérico (Fallback) ---
            'ulti_default': 'ulti.wav', 

            # --- Ultis Específicas (NUEVO) ---
            'ulti_curie': 'ulti_curie.wav',     # Sonido nuclear/radiación
            'ulti_einstein': 'ulti_einstein.wav', # Sonido de reloj/tiempo
            'ulti_gauss': 'ulti_gauss.wav',     # Sonido magnético/eléctrico
            'ulti_steve': 'ulti_steve.wav',     # Sonido de poner bloques (Minecraft)
            'ulti_tesla': 'ulti_tesla.wav'      # Sonido de rayo/teleport
        }
        
        self.cargar_sfx()

    def cargar_sfx(self):
        # (Este método queda igual, cargará automáticamente las nuevas entradas)
        for nombre, archivo in self.lista_archivos.items():
            ruta = os.path.join("assets", "sounds", archivo)
            if not os.path.exists(ruta):
                ruta = archivo
            
            if os.path.exists(ruta) and not archivo.endswith('.mp3'):
                try:
                    sfx = pygame.mixer.Sound(ruta)
                    sfx.set_volume(0.4)
                    self.sonidos[nombre] = sfx
                except:
                    pass 

    def play_sfx(self, nombre):
        if nombre in self.sonidos:
            self.sonidos[nombre].play()
        # Fallback: Si intentas tocar una ulti específica que no existe, toca la default
        elif nombre.startswith('ulti_') and 'ulti_default' in self.sonidos:
             self.sonidos['ulti_default'].play()

    def play_musica(self, nombre):
        nombre_archivo = self.lista_archivos.get(nombre)
        if not nombre_archivo: return
        ruta = os.path.join("assets", "sounds", nombre_archivo)
        if not os.path.exists(ruta): ruta = nombre_archivo
        if os.path.exists(ruta):
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except: pass

    def stop_musica(self):
        pygame.mixer.music.stop()