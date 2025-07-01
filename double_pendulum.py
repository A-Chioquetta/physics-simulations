import pygame
import sys
import math

# --- Configurações Iniciais ---
WIDTH, HEIGHT = 800, 600
FPS = 60 
DT = 1 / FPS 

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) # Bob 1
GREEN = (0, 255, 0) # Botão INICIAR
BLUE = (0, 0, 255) # Fio 1
CYAN = (0, 255, 255) # Bob 2
MAGENTA = (255, 0, 255) # Fio 2
YELLOW = (255, 255, 0) # Pivô

# Cores para InputBox
LIGHT_GREY = (200, 200, 200)
ACTIVE_COLOR = (150, 150, 255)
INACTIVE_COLOR = (100, 100, 100)

# Escala do Mundo Real para Pixels
PIXELS_PER_METER = 50 

# Inicializa o Pygame
pygame.init()
pygame.font.init() 

# Cria a tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulação de Pêndulo Duplo")

# Clock para controlar o FPS
clock = pygame.time.Clock()

# Gravidade no mundo real (m/s^2)
GRAVITY_REAL = 9.81 # m/s^2

# Ponto de Pivô do Pêndulo (fixo na tela)
pivot_point_pixel = (WIDTH // 2, 100)


class InputBox:
    def __init__(self, x, y, w, h, text='', label=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INACTIVE_COLOR 
        self.text = text
        self.label = label
        self.font = pygame.font.Font(None, 24)
        self.active = False
        self.txt_surface = self.font.render(text, True, LIGHT_GREY)
        self.label_surface = self.font.render(label, True, WHITE)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = ACTIVE_COLOR if self.active else INACTIVE_COLOR
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = INACTIVE_COLOR
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isdigit() or \
                       (event.unicode == '.' and '.' not in self.text) or \
                       (event.unicode == '-' and not self.text and len(self.text) == 0):
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, LIGHT_GREY)

    def draw(self, screen):
        screen.blit(self.label_surface, (self.rect.x - self.label_surface.get_width() - 5, self.rect.y + (self.rect.height - self.label_surface.get_height()) // 2))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return 0.0

# --- Variáveis do Pêndulo Duplo (globais) ---
L1_real = 0.0
L2_real = 0.0
M1_real = 0.0
M2_real = 0.0

# Ângulos e Velocidades Angulares (em radianos)
theta1_radians = 0.0
omega1_radians_per_sec = 0.0 # d(theta1)/dt
alpha1_radians_per_sec2 = 0.0 # d(omega1)/dt

theta2_radians = 0.0
omega2_radians_per_sec = 0.0 # d(theta2)/dt
alpha2_radians_per_sec2 = 0.0 # d(omega2)/dt

# Posições dos bobs (em pixels)
bob1_pos_pixel = (0, 0)
bob2_pos_pixel = (0, 0)

bob_radius_pixel = 10 # Raio dos bobs em pixels

is_simulating = False
time_since_launch = 0.0

# Para desenhar a trajetória do segundo bob 
trajectory_points_bob2 = []
MAX_TRAJECTORY_POINTS = 2000 # Limite de pontos para não sobrecarregar a memória

# --- Instâncias das Caixas de Input ---
input_box_L1 = InputBox(WIDTH - 150, 10, 140, 32, '2.0', 'Comp. 1 (m):')
input_box_M1 = InputBox(WIDTH - 150, 50, 140, 32, '1.0', 'Massa 1 (kg):')
input_box_theta1 = InputBox(WIDTH - 150, 90, 140, 32, '90.0', 'Ângulo 1 (gr):') 

input_box_L2 = InputBox(WIDTH - 150, 150, 140, 32, '2.0', 'Comp. 2 (m):')
input_box_M2 = InputBox(WIDTH - 150, 190, 140, 32, '1.0', 'Massa 2 (kg):')
input_box_theta2 = InputBox(WIDTH - 150, 230, 140, 32, '0.0', 'Ângulo 2 (gr):') 

input_boxes = [input_box_L1, input_box_M1, input_box_theta1,
               input_box_L2, input_box_M2, input_box_theta2]


# --- Função para Resetar o Pêndulo Duplo ---
def reset_double_pendulum(reset_inputs=False):
    global L1_real, L2_real, M1_real, M2_real, \
           theta1_radians, omega1_radians_per_sec, \
           theta2_radians, omega2_radians_per_sec, \
           bob1_pos_pixel, bob2_pos_pixel, is_simulating, time_since_launch, \
           trajectory_points_bob2

    if reset_inputs:
        input_box_L1.text = '2.0'
        input_box_M1.text = '1.0'
        input_box_theta1.text = '90.0'
        input_box_L2.text = '2.0'
        input_box_M2.text = '1.0'
        input_box_theta2.text = '0.0'
        
    
        for box in input_boxes:
            box.txt_surface = box.font.render(box.text, True, LIGHT_GREY)

   
    L1_real = input_box_L1.get_value()
    M1_real = input_box_M1.get_value()
    initial_theta1_degrees = input_box_theta1.get_value()

    L2_real = input_box_L2.get_value()
    M2_real = input_box_M2.get_value()
    initial_theta2_degrees = input_box_theta2.get_value()

    # Converte ângulos iniciais para radianos
    theta1_radians = math.radians(initial_theta1_degrees)
    theta2_radians = math.radians(initial_theta2_degrees)
    
    # Zera velocidades angulares
    omega1_radians_per_sec = 0.0
    omega2_radians_per_sec = 0.0

    is_simulating = False
    time_since_launch = 0.0
    trajectory_points_bob2.clear()

    # Bob 1
    bob1_x_pixel = pivot_point_pixel[0] + L1_real * PIXELS_PER_METER * math.sin(theta1_radians)
    bob1_y_pixel = pivot_point_pixel[1] + L1_real * PIXELS_PER_METER * math.cos(theta1_radians)
    bob1_pos_pixel = (int(bob1_x_pixel), int(bob1_y_pixel))

    # Bob 2
    bob2_x_pixel = bob1_pos_pixel[0] + L2_real * PIXELS_PER_METER * math.sin(theta2_radians)
    bob2_y_pixel = bob1_pos_pixel[1] + L2_real * PIXELS_PER_METER * math.cos(theta2_radians)
    bob2_pos_pixel = (int(bob2_x_pixel), int(bob2_y_pixel))



# --- Função para Iniciar a Simulação ---
def start_simulation():

    global is_simulating
    reset_double_pendulum(reset_inputs=False)

    # Validação mínima
    if L1_real > 0 and L2_real > 0 and M1_real > 0 and M2_real > 0:
        is_simulating = True
    else:
        print("Valores de entrada inválidos para simulação (comprimentos e massas devem ser > 0).")
        is_simulating = False


# Botão de Iniciar
start_button_rect = pygame.Rect(WIDTH - 150, 270, 140, 40) # Posição ajustada
start_button_text = pygame.font.Font(None, 30).render("INICIAR", True, BLACK)

# --- Função para renderizar texto na tela ---
def draw_text(surface, text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


# --- Inicializa o pêndulo (para o estado inicial ao abrir o programa) ---
reset_double_pendulum(reset_inputs=True)

# --- Loop Principal do Jogo ---
running = True
while running:
    # 1. Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        

        for box in input_boxes:
            box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                start_simulation()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: 
                reset_double_pendulum(reset_inputs=False) 


    # 2. Atualização
    if is_simulating:
        
       
        delta_theta = theta1_radians - theta2_radians
        sum_mass = M1_real + M2_real

        # Denominador comum para ambas as acelerações
        den = (2 * M1_real + M2_real - M2_real * math.cos(2 * delta_theta))
        if den == 0: 
            den = 1e-9 

        # Aceleração Angular do Pêndulo 1 
        num1_term1 = -GRAVITY_REAL * (2 * M1_real + M2_real) * math.sin(theta1_radians)
        num1_term2 = -M2_real * GRAVITY_REAL * math.sin(theta1_radians - 2 * theta2_radians)
        num1_term3 = -2 * M2_real * math.sin(delta_theta) * (omega2_radians_per_sec**2 * L2_real + omega1_radians_per_sec**2 * L1_real * math.cos(delta_theta))
        alpha1_radians_per_sec2 = (num1_term1 + num1_term2 + num1_term3) / (L1_real * den)

        # Aceleração Angular do Pêndulo 2 
        num2_term1 = 2 * math.sin(delta_theta)
        num2_term2 = (omega1_radians_per_sec**2 * L1_real * sum_mass + GRAVITY_REAL * sum_mass * math.cos(theta1_radians) + omega2_radians_per_sec**2 * L2_real * M2_real * math.cos(delta_theta))
        alpha2_radians_per_sec2 = (num2_term1 * num2_term2) / (L2_real * den)


        # Atualiza velocidades e ângulos (Método de Euler Simples)
        omega1_radians_per_sec += alpha1_radians_per_sec2 * DT
        theta1_radians += omega1_radians_per_sec * DT

        omega2_radians_per_sec += alpha2_radians_per_sec2 * DT
        theta2_radians += omega2_radians_per_sec * DT

        
        time_since_launch += DT

        
        bob1_x_pixel = pivot_point_pixel[0] + L1_real * PIXELS_PER_METER * math.sin(theta1_radians)
        bob1_y_pixel = pivot_point_pixel[1] + L1_real * PIXELS_PER_METER * math.cos(theta1_radians)
        bob1_pos_pixel = (int(bob1_x_pixel), int(bob1_y_pixel))

        bob2_x_pixel = bob1_pos_pixel[0] + L2_real * PIXELS_PER_METER * math.sin(theta2_radians)
        bob2_y_pixel = bob1_pos_pixel[1] + L2_real * PIXELS_PER_METER * math.cos(theta2_radians)
        bob2_pos_pixel = (int(bob2_x_pixel), int(bob2_y_pixel))

       
        trajectory_points_bob2.append(bob2_pos_pixel)
        if len(trajectory_points_bob2) > MAX_TRAJECTORY_POINTS:
            trajectory_points_bob2.pop(0)


    # 3. Desenho
    screen.fill(BLACK) 

    # Desenha o rastro do segundo bob
    if len(trajectory_points_bob2) > 1:
        pygame.draw.lines(screen, WHITE, False, trajectory_points_bob2, 1) 

    # Desenha o ponto de pivô
    pygame.draw.circle(screen, YELLOW, pivot_point_pixel, 5)

    # Desenha o primeiro fio e bob
    pygame.draw.line(screen, BLUE, pivot_point_pixel, bob1_pos_pixel, 2)
    pygame.draw.circle(screen, RED, bob1_pos_pixel, bob_radius_pixel)

    # Desenha o segundo fio e bob
    pygame.draw.line(screen, MAGENTA, bob1_pos_pixel, bob2_pos_pixel, 2)
    pygame.draw.circle(screen, CYAN, bob2_pos_pixel, bob_radius_pixel)


    # Desenha as caixas de input
    for box in input_boxes:
        box.draw(screen)
    
    # Desenha o botão de Iniciar
    pygame.draw.rect(screen, GREEN, start_button_rect)
    screen.blit(start_button_text, (start_button_rect.x + (start_button_rect.width - start_button_text.get_width()) // 2,
                                     start_button_rect.y + (start_button_rect.height - start_button_text.get_height()) // 2))


    # --- Exibir Parâmetros ---
    draw_text(screen, f"L1: {L1_real:.2f}m, M1: {M1_real:.2f}kg", 20, WHITE, 10, 10)
    draw_text(screen, f"L2: {L2_real:.2f}m, M2: {M2_real:.2f}kg", 20, WHITE, 10, 30)
    
    draw_text(screen, f"Theta1: {math.degrees(theta1_radians):.2f}°", 20, WHITE, 10, 60)
    draw_text(screen, f"Omega1: {math.degrees(omega1_radians_per_sec):.2f}°/s", 20, WHITE, 10, 80)
    
    draw_text(screen, f"Theta2: {math.degrees(theta2_radians):.2f}°", 20, WHITE, 10, 110)
    draw_text(screen, f"Omega2: {math.degrees(omega2_radians_per_sec):.2f}°/s", 20, WHITE, 10, 130)

    draw_text(screen, f"Tempo Total: {time_since_launch:.2f}s", 20, WHITE, 10, 160)
    draw_text(screen, "Pressione 'R' para Resetar", 20, WHITE, 10, HEIGHT - 30)



    pygame.display.flip()


    clock.tick(FPS)


pygame.quit()
sys.exit()