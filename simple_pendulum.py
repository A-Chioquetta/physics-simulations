import pygame
import sys
import math

# --- Configurações Iniciais ---
WIDTH, HEIGHT = 800, 600
FPS = 60 # Frames por segundo
DT = 1 / FPS # Delta de tempo em segundos por frame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) # Bob do Pêndulo
GREEN = (0, 255, 0) # Botão INICIAR
BLUE = (0, 0, 255) # Fio do Pêndulo
YELLOW = (255, 255, 0) # Pivô do Pêndulo
LIGHT_GREY = (200, 200, 200) # Cor para texto input
ACTIVE_COLOR = (150, 150, 255) # Cor quando a caixa de input está ativa
INACTIVE_COLOR = (100, 100, 100) # Cor quando a caixa de input está inativa

# --- Escala do Mundo Real para Pixels ---
PIXELS_PER_METER = 50 # 1 metro = 50 pixels (ajuste conforme necessário)

# Inicializa o Pygame
pygame.init()
pygame.font.init() # Inicializa o módulo de fontes

# Cria a tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulação de Pêndulo Simples com Energia")

# Clock para controlar o FPS
clock = pygame.time.Clock()

# --- Gravidade no mundo real (m/s^2) ---
GRAVITY_REAL = 9.81 # m/s^2

# --- Ponto de Pivô do Pêndulo (fixo na tela) ---
pivot_point_pixel = (WIDTH // 2, 100) # Centro superior da tela

# --- CLASSE INPUTBOX ---
class InputBox:
    def __init__(self, x, y, w, h, text='', label=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INACTIVE_COLOR
        self.text = text
        self.label = label # Rótulo para a caixa de input (ex: "Velocidade:")
        self.font = pygame.font.Font(None, 24) # Fonte para o texto
        self.active = False
        self.txt_surface = self.font.render(text, True, LIGHT_GREY) # Superfície do texto
        self.label_surface = self.font.render(label, True, WHITE) # Superfície do rótulo

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Se o usuário clicou na caixa de input
            if self.rect.collidepoint(event.pos):
                self.active = not self.active # Alterna o estado ativo
            else:
                self.active = False
            self.color = ACTIVE_COLOR if self.active else INACTIVE_COLOR
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN: # Se Enter for pressionado
                    self.active = False # Desativa a caixa
                    self.color = INACTIVE_COLOR
                elif event.key == pygame.K_BACKSPACE: # Se Backspace for pressionado
                    self.text = self.text[:-1]
                else:
                    # Permite apenas números, ponto decimal e sinal de menos (para alturas ou ângulos negativos)
                    if event.unicode.isdigit() or \
                       (event.unicode == '.' and '.' not in self.text) or \
                       (event.unicode == '-' and not self.text and len(self.text) == 0):
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, LIGHT_GREY)

    def draw(self, screen):
        # Desenha o rótulo
        screen.blit(self.label_surface, (self.rect.x - self.label_surface.get_width() - 5, self.rect.y + (self.rect.height - self.label_surface.get_height()) // 2))
        # Desenha a caixa de input
        pygame.draw.rect(screen, self.color, self.rect, 2) # Borda da caixa
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5)) # Texto dentro da caixa

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return 0.0 # Retorna 0 se o texto não for um número válido (ou vazio)

# --- Variáveis do Pêndulo (globais para fácil acesso) ---
pendulum_length_real = 0.0 # Comprimento do fio em metros
pendulum_mass_real = 0.0 # Massa do bob em kg (NOVA VARIÁVEL)
initial_angle_degrees = 0.0 # Ângulo inicial em graus (da vertical, positivo para direita)

current_angle_radians = 0.0 # Ângulo atual em radianos (da vertical)
angular_velocity_radians_per_sec = 0.0 # Velocidade angular em radianos/segundo

bob_pos_pixel = (0, 0) # Posição atual do bob (massa) em pixels
bob_radius_pixel = 15 # Raio do círculo que representa o bob

is_simulating = False # Flag para controlar se a simulação está rodando

# --- Variáveis para cálculo de parâmetros ---
max_angle_reached_radians = 0.0 # Para rastrear a amplitude máxima (se diminuir por amortecimento)
time_since_launch = 0.0

# --- Instâncias das Caixas de Input ---
# Posição x, y, largura, altura, texto inicial, rótulo
input_box_length = InputBox(WIDTH - 150, 10, 140, 32, '5.0', 'Comprimento (m):')
input_box_angle = InputBox(WIDTH - 150, 50, 140, 32, '45.0', 'Ângulo Inicial (gr):')
input_box_mass = InputBox(WIDTH - 150, 90, 140, 32, '1.0', 'Massa (kg):') # NOVA CAIXA DE INPUT

input_boxes = [input_box_length, input_box_angle, input_box_mass]


# --- Função para Resetar o Pêndulo ao estado pré-lançamento ---
# reset_inputs=True: Define o texto das caixas para valores padrão
# reset_inputs=False: Lê os valores atuais das caixas
def reset_pendulum(reset_inputs=False):
    # print(f"--- DEBUG: reset_pendulum() chamado (reset_inputs={reset_inputs}) ---") # Ative para debug
    global pendulum_length_real, pendulum_mass_real, initial_angle_degrees, \
           current_angle_radians, angular_velocity_radians_per_sec, \
           bob_pos_pixel, is_simulating, max_angle_reached_radians, time_since_launch

    # Se 'reset_inputs' for True, redefine o texto das caixas de input para valores padrão
    if reset_inputs:
        input_box_length.text = '5.0'
        input_box_angle.text = '45.0'
        input_box_mass.text = '1.0' # Reseta massa
        
        # Atualiza a superfície de texto das caixas para exibir os novos valores
        input_box_length.txt_surface = input_box_length.font.render(input_box_length.text, True, LIGHT_GREY)
        input_box_angle.txt_surface = input_box_angle.font.render(input_box_angle.text, True, LIGHT_GREY)
        input_box_mass.txt_surface = input_box_mass.font.render(input_box_mass.text, True, LIGHT_GREY)


    # Pega os valores dos inputs
    pendulum_length_real = input_box_length.get_value()
    pendulum_mass_real = input_box_mass.get_value() # LÊ MASSA
    initial_angle_degrees = input_box_angle.get_value()

    # Converte ângulo inicial para radianos
    current_angle_radians = math.radians(initial_angle_degrees)
    angular_velocity_radians_per_sec = 0.0 # Começa do repouso

    is_simulating = False # Simulação não está rodando após o reset
    max_angle_reached_radians = abs(current_angle_radians) # A amplitude máxima inicial é o ângulo de lançamento
    time_since_launch = 0.0

    # Calcula a posição inicial do bob (para desenhar no estado de repouso)
    bob_x_pixel = pivot_point_pixel[0] + pendulum_length_real * PIXELS_PER_METER * math.sin(current_angle_radians)
    bob_y_pixel = pivot_point_pixel[1] + pendulum_length_real * PIXELS_PER_METER * math.cos(current_angle_radians)
    bob_pos_pixel = (int(bob_x_pixel), int(bob_y_pixel))

    # print(f"DEBUG: Pendulum Reset - Length: {pendulum_length_real:.2f}m, Angle: {initial_angle_degrees:.2f}deg, Mass: {pendulum_mass_real:.2f}kg") # Ative para debug


# --- Função para Iniciar a Simulação ---
def start_simulation():
    # print("\n--- DEBUG: start_simulation() chamado ---") # Ative para debug
    global is_simulating
    # Sempre resetamos o estado do pêndulo antes de iniciar para usar os inputs mais recentes
    reset_pendulum(reset_inputs=False)

    # Verifica se os valores são válidos para iniciar a simulação
    if pendulum_length_real > 0 and pendulum_mass_real > 0 and abs(initial_angle_degrees) <= 170: # Ângulo não pode ser 180 ou 0 para começar a balançar
        is_simulating = True
    else:
        print("Valores de entrada inválidos para simulação (comprimento > 0, massa > 0, ângulo entre -170 e 170).")
        is_simulating = False # Garante que não inicia se inválido
    # print("------------------------------------") # Ative para debug


# Botão de Lançamento
start_button_rect = pygame.Rect(WIDTH - 150, 130, 140, 40)
start_button_text = pygame.font.Font(None, 30).render("INICIAR", True, BLACK)

# --- Função para renderizar texto na tela ---
def draw_text(surface, text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


# --- Inicializa o pêndulo (para o estado inicial ao abrir o programa) ---
# Chamamos com reset_inputs=True para definir os valores padrão nas caixas de input
reset_pendulum(reset_inputs=True)

# --- Loop Principal do Jogo ---
running = True
while running:
    # 1. Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Passa o evento para cada caixa de input
        for box in input_boxes:
            box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Se clicou no botão de iniciar simulação
            if start_button_rect.collidepoint(event.pos):
                start_simulation()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Se a tecla 'R' for pressionada
                # print("\n--- DEBUG: Tecla 'R' pressionada! ---") # Ative para debug
                # Chama reset_pendulum para redefinir o estado da simulação,
                # mantendo os valores ATUAIS das caixas de input.
                reset_pendulum(reset_inputs=False) 
                # print(f"DEBUG: Após reset_pendulum() chamado por 'R':") # Ative para debug


    # 2. Atualização (Lógica da Física do Pêndulo)
    if is_simulating:
        # ----------------------------------------------------
        # Equações de Movimento do Pêndulo Simples (sem amortecimento)
        # Aceleração angular = -(gravidade / comprimento) * sen(ângulo)
        # ----------------------------------------------------
        
        # Aceleração angular em radianos/segundo^2
        angular_acceleration = -(GRAVITY_REAL / pendulum_length_real) * math.sin(current_angle_radians)

        # Atualiza a velocidade angular (Euler simples)
        angular_velocity_radians_per_sec += angular_acceleration * DT

        # Atualiza o ângulo (Euler simples)
        current_angle_radians += angular_velocity_radians_per_sec * DT

        # Atualiza o tempo de simulação
        time_since_launch += DT

        # Atualiza a posição do bob
        bob_x_pixel = pivot_point_pixel[0] + pendulum_length_real * PIXELS_PER_METER * math.sin(current_angle_radians)
        bob_y_pixel = pivot_point_pixel[1] + pendulum_length_real * PIXELS_PER_METER * math.cos(current_angle_radians)
        bob_pos_pixel = (int(bob_x_pixel), int(bob_y_pixel))

    # 3. Desenho
    screen.fill(BLACK) # Preenche a tela com preto a cada frame

    # Desenha o ponto de pivô
    pygame.draw.circle(screen, YELLOW, pivot_point_pixel, 5)

    # Desenha o fio do pêndulo (do pivô ao bob)
    pygame.draw.line(screen, BLUE, pivot_point_pixel, bob_pos_pixel, 2)

    # Desenha o bob do pêndulo
    pygame.draw.circle(screen, RED, bob_pos_pixel, bob_radius_pixel)


    # Desenha as caixas de input
    for box in input_boxes:
        box.draw(screen)
    
    # Desenha o botão de Iniciar
    pygame.draw.rect(screen, GREEN, start_button_rect)
    screen.blit(start_button_text, (start_button_rect.x + (start_button_rect.width - start_button_text.get_width()) // 2,
                                     start_button_rect.y + (start_button_rect.height - start_button_text.get_height()) // 2))


    # --- Exibir Parâmetros e Energias ---
    # Converte radianos para graus para exibição
    current_angle_degrees_display = math.degrees(current_angle_radians)
    angular_velocity_degrees_per_sec_display = math.degrees(angular_velocity_radians_per_sec)

    # --- CÁLCULO DAS ENERGIAS ---
    # Energia Potencial (PE)
    # Ponto mais baixo (referência para h=0): bob estaria em (pivot_x, pivot_y + L_pixel)
    lowest_bob_y_pixel = pivot_point_pixel[1] + pendulum_length_real * PIXELS_PER_METER
    height_from_lowest_pixel = lowest_bob_y_pixel - bob_pos_pixel[1] # Diferença positiva para cima
    height_from_lowest_real = height_from_lowest_pixel / PIXELS_PER_METER
    potential_energy = pendulum_mass_real * GRAVITY_REAL * height_from_lowest_real

    # Energia Cinética (KE)
    # Velocidade linear = comprimento * velocidade angular
    linear_velocity_real = pendulum_length_real * angular_velocity_radians_per_sec
    kinetic_energy = 0.5 * pendulum_mass_real * (linear_velocity_real ** 2)

    # Energia Total (TE)
    total_energy = potential_energy + kinetic_energy


    draw_text(screen, f"Comprimento: {pendulum_length_real:.2f}m", 20, WHITE, 10, 10)
    draw_text(screen, f"Massa: {pendulum_mass_real:.2f}kg", 20, WHITE, 10, 30) # Nova linha
    draw_text(screen, f"Ângulo Atual: {current_angle_degrees_display:.2f}°", 20, WHITE, 10, 50)
    draw_text(screen, f"Vel. Angular: {angular_velocity_degrees_per_sec_display:.2f}°/s", 20, WHITE, 10, 70)
    draw_text(screen, f"Tempo Total: {time_since_launch:.2f}s", 20, WHITE, 10, 90)

    # Exibição das Energias
    draw_text(screen, f"Energia Potencial: {potential_energy:.2f} J", 20, WHITE, 10, 120)
    draw_text(screen, f"Energia Cinética: {kinetic_energy:.2f} J", 20, WHITE, 10, 140)
    draw_text(screen, f"Energia Total: {total_energy:.2f} J", 20, WHITE, 10, 160)

    draw_text(screen, "Pressione 'R' para Resetar", 20, WHITE, 10, HEIGHT - 30)


    # Atualiza a tela
    pygame.display.flip()

    # Controla o FPS
    clock.tick(FPS)

# Sai do Pygame
pygame.quit()
sys.exit()