import pygame
import sys
import math

# --- Configurações Iniciais ---
WIDTH, HEIGHT = 800, 600
FPS = 60 # Frames por segundo
DT = 1 / FPS # Delta de tempo em segundos por frame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) # Projétil e seta Vx
GREEN = (0, 255, 0) # Chão e botão LANÇAR
BLUE = (0, 0, 255) # Trajetória
YELLOW = (255, 255, 0) # Seta Vy (NOVA COR)
LIGHT_GREY = (200, 200, 200) # Cor para texto input
ACTIVE_COLOR = (150, 150, 255) # Cor quando a caixa de input está ativa
INACTIVE_COLOR = (100, 100, 100) # Cor quando a caixa de input está inativa

# --- Escala do Mundo Real para Pixels ---
PIXELS_PER_METER = 50 # 1 metro = 50 pixels

# Inicializa o Pygame
pygame.init()
pygame.font.init() # Inicializa o módulo de fontes

# Cria a tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulação de Projétil com Vetores de Velocidade")

# Clock para controlar o FPS
clock = pygame.time.Clock()

# --- Gravidade no mundo real (m/s^2) ---
GRAVITY_REAL = 9.81 # m/s^2
GRAVITY_PIXEL_PER_SEC2 = GRAVITY_REAL * PIXELS_PER_METER

# --- Posição do chão em pixels ---
ground_y_pixel = HEIGHT - 40

# --- Classe para Caixa de Input de Texto ---
class InputBox:
    def __init__(self, x, y, w, h, text='', label=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INACTIVE_COLOR
        self.text = text
        self.label = label 
        self.font = pygame.font.Font(None, 32) 
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
                    if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text) or (event.unicode == '-' and not self.text and len(self.text) == 0):
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, LIGHT_GREY)

    def draw(self, screen):
        # Desenha o rótulo
        screen.blit(self.label_surface, (self.rect.x - self.label_surface.get_width() - 5, self.rect.y + (self.rect.height - self.label_surface.get_height()) // 2))
        pygame.draw.rect(screen, self.color, self.rect, 2) # Borda da caixa
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5)) # Texto dentro da caixa

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return 0.0 

# --- Variáveis do Projétil (globais para fácil acesso) ---
projectile_x_pixel = 0
projectile_y_pixel = 0
velocity_x_pixel_per_sec = 0
velocity_y_pixel_per_sec = 0
is_launched = False 

trajectory_points = []

# --- Variáveis para cálculo de parâmetros ---
max_height_reached_pixel = 0 
initial_launch_x_pixel = 0
initial_launch_y_pixel = 0 

time_in_air = 0.0

# --- Instâncias das Caixas de Input ---
input_box_vel = InputBox(WIDTH - 150, 10, 140, 32, '10.0', 'Vel. Inicial (m/s):')
input_box_angle = InputBox(WIDTH - 150, 50, 140, 32, '45.0', 'Ângulo (graus):')
input_box_height = InputBox(WIDTH - 150, 90, 140, 32, '0.5', 'Altura Inicial (m):')

input_boxes = [input_box_vel, input_box_angle, input_box_height]


# --- Função para Resetar o Projétil ao estado pré-lançamento ---
def reset_projectile(reset_inputs=False):
    global projectile_x_pixel, projectile_y_pixel, velocity_x_pixel_per_sec, \
           velocity_y_pixel_per_sec, is_launched, trajectory_points, \
           max_height_reached_pixel, initial_launch_x_pixel, initial_launch_y_pixel, time_in_air

    if reset_inputs:
        input_box_vel.text = '10.0'
        input_box_angle.text = '45.0'
        input_box_height.text = '0.5'
        
        # Atualiza a superfície de texto das caixas para exibir os novos valores
        input_box_vel.txt_surface = input_box_vel.font.render(input_box_vel.text, True, LIGHT_GREY)
        input_box_angle.txt_surface = input_box_angle.font.render(input_box_angle.text, True, LIGHT_GREY)
        input_box_height.txt_surface = input_box_height.font.render(input_box_height.text, True, LIGHT_GREY)


    # Pega os valores dos inputs
    initial_vel_real = input_box_vel.get_value()
    launch_angle_degrees = input_box_angle.get_value()
    initial_height_real = input_box_height.get_value()

    # Converte ângulo para radianos
    launch_angle_radians = math.radians(launch_angle_degrees)

    # Calcula componentes da velocidade em m/s
    initial_velocity_x_real = initial_vel_real * math.cos(launch_angle_radians)
    initial_velocity_y_real = initial_vel_real * math.sin(launch_angle_radians)

    # Converte para pixels/segundo
    velocity_x_pixel_per_sec = initial_velocity_x_real * PIXELS_PER_METER
    velocity_y_pixel_per_sec = -initial_velocity_y_real * PIXELS_PER_METER 

    # Define a posição inicial do projétil em pixels
    initial_launch_x_pixel = 50 
    initial_launch_y_pixel = ground_y_pixel - (initial_height_real * PIXELS_PER_METER)

    projectile_x_pixel = initial_launch_x_pixel
    projectile_y_pixel = initial_launch_y_pixel

    is_launched = False 
    trajectory_points.clear() 

    max_height_reached_pixel = initial_launch_y_pixel

    time_in_air = 0.0

# --- Função para Iniciar o Lançamento ---
def start_launch():
    global is_launched

    reset_projectile(reset_inputs=False) 

    initial_vel_real = input_box_vel.get_value()
    launch_angle_degrees = input_box_angle.get_value()

    if initial_vel_real > 0 and launch_angle_degrees >= 0 and launch_angle_degrees <= 90:
        is_launched = True
        trajectory_points.append((int(projectile_x_pixel), int(projectile_y_pixel)))
    else:
        print("Valores de entrada inválidos para lançamento (velocidade > 0, ângulo entre 0 e 90).")
        is_launched = False 


# Botão de Lançamento
launch_button_rect = pygame.Rect(WIDTH - 150, 130, 140, 40)
launch_button_text = pygame.font.Font(None, 30).render("LANÇAR", True, BLACK)

# --- Função para renderizar texto na tela ---
def draw_text(surface, text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

# --- DESENHAR SETAS ---
def draw_arrow(surface, color, start_point, end_point, width, arrow_head_size):
    
    pygame.draw.line(surface, color, start_point, end_point, width)
    angle = math.atan2(start_point[1] - end_point[1], start_point[0] - end_point[0])
    end_point_x, end_point_y = end_point

    pygame.draw.polygon(surface, color, [
        end_point,
        (end_point_x + arrow_head_size * math.cos(angle + math.pi / 6),
         end_point_y + arrow_head_size * math.sin(angle + math.pi / 6)),
        (end_point_x + arrow_head_size * math.cos(angle - math.pi / 6),
         end_point_y + arrow_head_size * math.sin(angle - math.pi / 6))
    ])


# --- Inicializa o projétil no reset  ---
reset_projectile(reset_inputs=True)

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
            # Se clicou no botão de lançamento
            if launch_button_rect.collidepoint(event.pos):
                start_launch()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Se a tecla 'R' for pressionada
                reset_projectile(reset_inputs=False) 



    # 2. Atualização (Lógica da Física)
    if is_launched:
        velocity_y_pixel_per_sec += GRAVITY_PIXEL_PER_SEC2 * DT

        # Atualiza a posição (em pixels)
        projectile_x_pixel += velocity_x_pixel_per_sec * DT
        projectile_y_pixel += velocity_y_pixel_per_sec * DT

        # Adiciona o ponto atual à trajetória
        trajectory_points.append((int(projectile_x_pixel), int(projectile_y_pixel)))
        if len(trajectory_points) > 1000: 
            trajectory_points.pop(0)

        if projectile_y_pixel < max_height_reached_pixel:
             max_height_reached_pixel = projectile_y_pixel
        
        # Atualiza o tempo de voo
        time_in_air += DT

        if projectile_y_pixel >= ground_y_pixel and initial_launch_y_pixel < ground_y_pixel:
            projectile_y_pixel = ground_y_pixel 
            velocity_x_pixel_per_sec = 0   
            velocity_y_pixel_per_sec = 0     
            is_launched = False 
   
            if len(trajectory_points) > 0:
                trajectory_points[-1] = (int(projectile_x_pixel), int(projectile_y_pixel))
        elif projectile_y_pixel >= ground_y_pixel and is_launched and initial_launch_y_pixel == ground_y_pixel and time_in_air > 0.1: # Pequeno tempo para garantir que subiu e desceu
            projectile_y_pixel = ground_y_pixel 
            velocity_x_pixel_per_sec = 0     
            velocity_y_pixel_per_sec = 0     
            is_launched = False 
            if len(trajectory_points) > 0:
                trajectory_points[-1] = (int(projectile_x_pixel), int(projectile_y_pixel))


    # 3. Desenho
    screen.fill(BLACK) 

    # Desenha o rastro da trajetória
    if len(trajectory_points) > 1:
        pygame.draw.lines(screen, BLUE, False, trajectory_points, 2)

    # Desenha o projétil (um círculo vermelho)
    if not is_launched:
        pygame.draw.circle(screen, RED, (int(initial_launch_x_pixel), int(initial_launch_y_pixel)), 10)
    else:
        pygame.draw.circle(screen, RED, (int(projectile_x_pixel), int(projectile_y_pixel)), 10)
        
        velocity_scale = 0.2 
        arrow_head_size = 7

        # Velocidade horizontal (eixo X)
        vx_component = velocity_x_pixel_per_sec * velocity_scale
        start_vx = (int(projectile_x_pixel), int(projectile_y_pixel))
        end_vx = (int(projectile_x_pixel + vx_component), int(projectile_y_pixel))
        if abs(vx_component) > 1:
            draw_arrow(screen, RED, start_vx, end_vx, 2, arrow_head_size)

        # Velocidade vertical (eixo Y)
        vy_component = velocity_y_pixel_per_sec * velocity_scale
        start_vy = (int(projectile_x_pixel), int(projectile_y_pixel))
        end_vy = (int(projectile_x_pixel), int(projectile_y_pixel + vy_component))
        if abs(vy_component) > 1: 
            draw_arrow(screen, YELLOW, start_vy, end_vy, 2, arrow_head_size)


    # Desenha o chão 
    pygame.draw.line(screen, GREEN, (0, ground_y_pixel), (WIDTH, ground_y_pixel), 5)

    # Desenha as caixas de input
    for box in input_boxes:
        box.draw(screen)
    
    # Desenha o botão de Lançamento
    pygame.draw.rect(screen, GREEN, launch_button_rect)
    screen.blit(launch_button_text, (launch_button_rect.x + (launch_button_rect.width - launch_button_text.get_width()) // 2,
                                     launch_button_rect.y + (launch_button_rect.height - launch_button_text.get_height()) // 2))


    # --- Exibir Parâmetros ---
    # Converte de pixels para metros para exibição
    current_x_real = projectile_x_pixel / PIXELS_PER_METER
    current_y_real = (ground_y_pixel - projectile_y_pixel) / PIXELS_PER_METER # Inverte Y

    # Calcula o alcance horizontal quando o projétil para
    horizontal_range_real = 0
    if not is_launched and len(trajectory_points) > 0: 
        impact_x = trajectory_points[-1][0]
        horizontal_range_real = (impact_x - initial_launch_x_pixel) / PIXELS_PER_METER
        if horizontal_range_real < 0: horizontal_range_real = 0 # Garante que não é negativo

    # Calcula a altura máxima alcançada em metros
    max_height_real = (ground_y_pixel - max_height_reached_pixel) / PIXELS_PER_METER
    
    initial_real_height_for_display = (ground_y_pixel - initial_launch_y_pixel) / PIXELS_PER_METER
    if max_height_real < initial_real_height_for_display:
        max_height_real = initial_real_height_for_display


    draw_text(screen, f"Pos (X, Y): ({current_x_real:.2f}m, {current_y_real:.2f}m)", 20, WHITE, 10, 10)
    draw_text(screen, f"Vel (Vx, Vy): ({velocity_x_pixel_per_sec/PIXELS_PER_METER:.2f}m/s, {-velocity_y_pixel_per_sec/PIXELS_PER_METER:.2f}m/s)", 20, WHITE, 10, 30)
    draw_text(screen, f"Tempo de Voo: {time_in_air:.2f}s", 20, WHITE, 10, 50)
    draw_text(screen, f"Alcance Horizontal: {horizontal_range_real:.2f}m", 20, WHITE, 10, 70)
    draw_text(screen, f"Altura Máxima: {max_height_real:.2f}m", 20, WHITE, 10, 90)
    draw_text(screen, "Pressione 'R' para Resetar", 20, WHITE, 10, HEIGHT - 30)


    # Atualiza a tela
    pygame.display.flip()

    # Controla o FPS
    clock.tick(FPS)


pygame.quit()
sys.exit()