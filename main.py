import pygame
import random
import sys
import math

# ================== INIT ==================
pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 900, 500
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("RUN, MAN! - Night Hardcore")

CLOCK = pygame.time.Clock()
FPS = 60
HIGH_SCORE = 0

# ================== ASSETS ==================
def carregar_img(caminho, escala):
    try:
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(img, escala)
    except:
        surf = pygame.Surface(escala, pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 50, 50), (0, 0, escala[0], escala[1]))
        return surf

PLAYER_IMG = carregar_img("imagens/player.png", (80, 80))
MOEDA_IMG = carregar_img("imagens/moeda.png", (40, 40))
OBST_IMG = carregar_img("imagens/obstaculo.png", (60, 60))

try:
    FUNDO_MENU = pygame.transform.scale(pygame.image.load("imagens/fundo.png").convert(), (LARGURA, ALTURA))
    FONTE_T = pygame.font.Font("imagens/pixel.ttf", 80)
    FONTE_H = pygame.font.Font("imagens/pixel.ttf", 30)
except:
    FUNDO_MENU = pygame.Surface((LARGURA, ALTURA)); FUNDO_MENU.fill((10, 10, 30))
    FONTE_T = pygame.font.SysFont("Arial", 80, True)
    FONTE_H = pygame.font.SysFont("Arial", 30, True)

try:
    SOM_MOEDA = pygame.mixer.Sound("musicas/moeda.wav")
    SOM_PERDER = pygame.mixer.Sound("musicas/game_over.wav")
    pygame.mixer.music.load("musicas/musica.mp3")
except:
    SOM_MOEDA = SOM_PERDER = None

# ================== CLASSES ==================

class Estrela:
    def __init__(self):
        self.reset()
        self.x = random.randint(0, LARGURA)

    def reset(self):
        self.x = LARGURA + random.randint(10, 100)
        self.y = random.randint(0, ALTURA - 150)
        self.vel = random.uniform(0.2, 0.6)

    def draw(self):
        self.x -= self.vel
        if self.x < -5: self.reset()
        pygame.draw.circle(TELA, (255, 255, 255), (int(self.x), int(self.y)), 1)

class DetalheChao:
    def __init__(self):
        self.x = random.randint(0, LARGURA)
        self.y = random.randint(ALTURA - 35, ALTURA - 5)
        self.largura = random.randint(5, 15)

    def update(self, vel):
        self.x -= vel
        if self.x < -20:
            self.x = LARGURA + 20
            self.y = random.randint(ALTURA - 35, ALTURA - 5)

    def draw(self):
        pygame.draw.line(TELA, (40, 80, 40), (self.x, self.y), (self.x + self.largura, self.y), 2)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(120, ALTURA - 140, 45, 65)
        self.vel_y = 0
        self.pulo_atual = 0 
        self.cargas_duplas = 3 
        self.max_cooldown = 5 * 60
        self.cooldown = 0

    def update(self):
        self.vel_y += 1.2
        self.rect.y += self.vel_y
        
        if self.rect.bottom >= ALTURA - 40:
            self.rect.bottom = ALTURA - 40
            self.vel_y = 0
            self.pulo_atual = 0

        if self.cooldown > 0:
            self.cooldown -= 1
            if self.cooldown <= 0:
                self.cargas_duplas = 3

    def jump(self):
        if self.pulo_atual == 0:
            self.vel_y = -17
            self.pulo_atual = 1
            return True
        elif self.pulo_atual == 1 and self.cargas_duplas > 0:
            self.vel_y = -15
            self.pulo_atual = 2
            self.cargas_duplas -= 1
            if self.cargas_duplas == 0:
                self.cooldown = self.max_cooldown
            return True
        return False

# ================== TELAS ==================

def menu():
    timer = 0
    while True:
        timer += 0.05
        TELA.blit(FUNDO_MENU, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        TELA.blit(overlay, (0,0))

        offset_y = math.sin(timer) * 15
        titulo = FONTE_T.render("RUN, MAN!", True, (255, 255, 255))
        rect_t = titulo.get_rect(center=(LARGURA//2, 180 + offset_y))
        sombra_t = FONTE_T.render("RUN, MAN!", True, (50, 50, 50))
        TELA.blit(sombra_t, rect_t.move(4, 4))
        TELA.blit(titulo, rect_t)

        brilho = int(155 + 100 * math.sin(timer * 2))
        txt_start = FONTE_H.render("PRESSIONE [ENTER] PARA CORRER", True, (brilho, brilho, 0))
        TELA.blit(txt_start, txt_start.get_rect(center=(LARGURA//2, 350)))
        
        txt_high = FONTE_H.render(f"RECORD: {HIGH_SCORE}", True, (200, 200, 200))
        TELA.blit(txt_high, (LARGURA//2 - txt_high.get_width()//2, 400))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: return
        
        pygame.display.flip()
        CLOCK.tick(60)

def jogo():
    global HIGH_SCORE
    if not pygame.mixer.music.get_busy():
        try: pygame.mixer.music.play(-1)
        except: pass

    player = Player()
    estrelas = [Estrela() for _ in range(60)]
    detalhes_chao = [DetalheChao() for _ in range(15)]
    obstaculos = []
    moedas = []
    pontos = 0
    velocidade = 6.5
    timer_spawn = 0

    while True:
        CLOCK.tick(FPS)
        TELA.fill((5, 5, 15)) 

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and (e.key in [pygame.K_SPACE, pygame.K_UP]):
                player.jump()

        # Desenhar Fundo
        for s in estrelas: s.draw()
        
        # Desenhar Chão Estático
        pygame.draw.rect(TELA, (20, 40, 20), (0, ALTURA - 40, LARGURA, 40))
        
        # Detalhes do chão em movimento
        for d in detalhes_chao:
            d.update(velocidade)
            d.draw()

        # Lógica Player
        player.update()
        TELA.blit(PLAYER_IMG, (player.rect.x - 15, player.rect.y - 10))

        # --- BARRA DE CARREGAMENTO SOBRE O PERSONAGEM ---
        if player.cooldown > 0:
            # Texto de Segundos
            segundos = f"{player.cooldown // 60 + 1}s"
            txt_s = FONTE_H.render(segundos, True, (255, 200, 0))
            TELA.blit(txt_s, (player.rect.centerx - 10, player.rect.top - 45))
            
            # Barra de progresso
            largura_b = 50
            progresso = (player.cooldown / player.max_cooldown) * largura_b
            pygame.draw.rect(TELA, (50, 50, 50), (player.rect.centerx - 25, player.rect.top - 15, largura_b, 6))
            pygame.draw.rect(TELA, (255, 215, 0), (player.rect.centerx - 25, player.rect.top - 15, largura_b - progresso, 6))

        # HUD de Cargas de Pulo (Canto)
        for i in range(3):
            cor = (0, 255, 255) if i < player.cargas_duplas else (100, 0, 0)
            if player.cooldown > 0: cor = (255, 165, 0) if (player.cooldown // 10) % 2 == 0 else (50, 0, 0)
            pygame.draw.circle(TELA, cor, (40 + (i * 30), 100), 8)

        # Dificuldade e Spawn
        velocidade += 0.0012
        timer_spawn += 1
        if timer_spawn > max(35, 85 - int(velocidade * 1.5)):
            if random.random() < 0.6:
                obstaculos.append(pygame.Rect(LARGURA + 50, ALTURA - 100, 50, 60))
            else:
                moedas.append(pygame.Rect(LARGURA + 50, random.randint(200, 360), 35, 35))
            timer_spawn = 0

        # Processar Obstáculos
        for obs in obstaculos[:]:
            obs.x -= velocidade
            TELA.blit(OBST_IMG, obs)
            if player.rect.colliderect(obs):
                if SOM_PERDER: SOM_PERDER.play()
                pygame.mixer.music.stop()
                if pontos > HIGH_SCORE: HIGH_SCORE = pontos
                return
            if obs.right < 0:
                obstaculos.remove(obs); pontos += 1

        # Processar Moedas
        for m in moedas[:]:
            m.x -= velocidade
            TELA.blit(MOEDA_IMG, m)
            if player.rect.colliderect(m):
                if SOM_MOEDA: SOM_MOEDA.play()
                pontos += 15
                moedas.remove(m)
            elif m.right < 0: moedas.remove(m)

        # HUD Pontos
        TELA.blit(FONTE_H.render(f"PONTOS: {pontos}", True, (255, 255, 255)), (25, 25))
        
        pygame.display.flip()

while True:
    menu()
    jogo()