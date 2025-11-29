import pygame
import os

class GestorSonidos:
    def __init__(self):
        # Inicializar mixer si no está inicializado
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.sonidos = {}
        
        # Diccionario: 'nombre_codigo': 'nombre_archivo.wav/mp3'
        # Puedes añadir tus propios archivos aquí
        self.lista_archivos = {
            'rebote': 'hit.wav',       # Golpe pared/paleta
            'gol': 'goal.wav',         # Gol
            'item': 'powerup.wav',     # Recoger item
            'ulti': 'ulti.wav',        # Activar poder especial
            'click': 'click.wav',      # Click en menú
            'musica_menu': 'menu.mp3', # Música de fondo menú
            'musica_juego': 'game.mp3' # Música de fondo juego
        }
        
        self.cargar_sfx()

    def cargar_sfx(self):
        # Intentar cargar los efectos de sonido
        for nombre, archivo in self.lista_archivos.items():
            ruta = os.path.join("assets", "sounds", archivo)
            # Si no está en subcarpeta, buscar en raíz
            if not os.path.exists(ruta):
                ruta = archivo
            
            # Solo cargamos si existe y NO es música (mp3 usualmente para música)
            if os.path.exists(ruta) and not archivo.endswith('.mp3'):
                try:
                    sfx = pygame.mixer.Sound(ruta)
                    sfx.set_volume(0.4) # Volumen efectos
                    self.sonidos[nombre] = sfx
                except:
                    pass # Si falla, seguimos sin ese sonido

    def play_sfx(self, nombre):
        """ Reproduce un efecto corto """
        if nombre in self.sonidos:
            self.sonidos[nombre].play()

    def play_musica(self, nombre):
        """ Carga y reproduce música en loop """
        nombre_archivo = self.lista_archivos.get(nombre)
        if not nombre_archivo: return

        ruta = os.path.join("assets", "sounds", nombre_archivo)
        if not os.path.exists(ruta):
            ruta = nombre_archivo
        
        if os.path.exists(ruta):
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.set_volume(0.3) # Volumen música más bajo
                pygame.mixer.music.play(-1) # -1 = Loop infinito
            except:
                print(f"No se pudo cargar música: {ruta}")

    def stop_musica(self):
        pygame.mixer.music.stop()