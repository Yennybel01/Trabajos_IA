import pygame
import sys
import math
import random
import time
from enum import Enum
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from collections import deque

# Inicializar Pygame
pygame.init()

# Constantes
CELL_SIZE = 32
MAZE_WIDTH = 19
MAZE_HEIGHT = 21
WINDOW_WIDTH = MAZE_WIDTH * CELL_SIZE + 300  # Espacio extra para panel de información
WINDOW_HEIGHT = MAZE_HEIGHT * CELL_SIZE + 50
FPS = 8

# Colores mejorados
COLORS = {
    'BLACK': (0, 0, 0),
    'BLUE': (0, 0, 139),
    'YELLOW': (255, 255, 0),
    'RED': (255, 0, 0),
    'PINK': (255, 184, 255),
    'CYAN': (0, 255, 255),
    'ORANGE': (255, 165, 0),
    'WHITE': (255, 255, 255),
    'GREEN': (0, 255, 0),
    'GRAY': (128, 128, 128),
    'DARK_BLUE': (0, 0, 100),
    'GOLD': (255, 215, 0),
    'PURPLE': (128, 0, 128)
}

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

@dataclass
class Ghost:
    pos: List[int]
    color: Tuple[int, int, int]
    mode: str = "chase"  # chase, scatter, frightened
    home_corner: Tuple[int, int] = (0, 0)
    
    def copy(self):
        return Ghost(self.pos[:], self.color, self.mode, self.home_corner)

class GameState:
    def __init__(self):
        # Laberinto más complejo y realista
        self.maze = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
            [0,3,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,3,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1,0],
            [0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0],
            [0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,0],
            [2,2,2,0,1,0,1,1,1,1,1,1,1,0,1,0,2,2,2],
            [0,0,0,0,1,0,1,0,0,2,0,0,1,0,1,0,0,0,0],
            [2,1,1,1,1,1,1,0,2,2,2,0,1,1,1,1,1,1,2],
            [0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0],
            [2,2,2,0,1,0,1,1,1,1,1,1,1,0,1,0,2,2,2],
            [0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,0],
            [0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0],
            [0,1,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,3,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,3,0],
            [0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        
        self.pacman_pos = [9, 15]
        self.ghosts = [
            Ghost([8, 9], COLORS['RED'], "chase", (0, 0)),
            Ghost([9, 9], COLORS['PINK'], "chase", (18, 0)),
            Ghost([10, 9], COLORS['CYAN'], "chase", (0, 20)),
            Ghost([11, 9], COLORS['ORANGE'], "chase", (18, 20)),
        ]
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.pellets_remaining = self.count_pellets()
        self.power_pellets_remaining = self.count_power_pellets()
        self.game_over = False
        self.pacman_wins = False
        self.power_mode = False
        self.power_timer = 0
        self.move_history = deque(maxlen=10)
        
    def count_pellets(self):
        return sum(row.count(1) for row in self.maze)
    
    def count_power_pellets(self):
        return sum(row.count(3) for row in self.maze)
    
    def is_valid_position(self, pos):
        x, y = pos
        return (0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT and 
                self.maze[y][x] != 0)
    
    def get_valid_moves(self, pos):
        moves = []
        x, y = pos
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            dx, dy = direction.value
            new_pos = [x + dx, y + dy]
            if self.is_valid_position(new_pos):
                moves.append(direction)
        return moves
    
    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def move_pacman(self, direction):
        if direction is None or direction == Direction.NONE:
            return
            
        dx, dy = direction.value
        new_x = self.pacman_pos[0] + dx
        new_y = self.pacman_pos[1] + dy
        
        if self.is_valid_position([new_x, new_y]):
            self.pacman_pos = [new_x, new_y]
            self.move_history.append((new_x, new_y))
            
            # Comer pellet normal
            if self.maze[new_y][new_x] == 1:
                self.score += 10
                self.maze[new_y][new_x] = 2
                self.pellets_remaining -= 1
            # Comer power pellet
            elif self.maze[new_y][new_x] == 3:
                self.score += 50
                self.maze[new_y][new_x] = 2
                self.power_pellets_remaining -= 1
                self.power_mode = True
                self.power_timer = 30  # 30 turnos de poder
                
                # Cambiar fantasmas a modo asustado
                for ghost in self.ghosts:
                    ghost.mode = "frightened"
    
    def move_ghost(self, ghost_idx, direction):
        if direction is None or ghost_idx >= len(self.ghosts):
            return
            
        ghost = self.ghosts[ghost_idx]
        dx, dy = direction.value
        new_x = ghost.pos[0] + dx
        new_y = ghost.pos[1] + dy
        
        if self.is_valid_position([new_x, new_y]):
            ghost.pos = [new_x, new_y]
    
    def update_power_mode(self):
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
                for ghost in self.ghosts:
                    ghost.mode = "chase"
    
    def check_collision(self):
        for ghost in self.ghosts:
            if self.pacman_pos == ghost.pos:
                if self.power_mode and ghost.mode == "frightened":
                    # Pacman come fantasma
                    self.score += 200
                    ghost.pos = [9, 9]  # Regresa a casa
                    ghost.mode = "chase"
                    return False
                else:
                    return True
        return False
    
    def is_terminal(self):
        if self.check_collision():
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                return True
            else:
                # Reiniciar posiciones
                self.pacman_pos = [9, 15]
                for i, ghost in enumerate(self.ghosts):
                    ghost.pos = [8 + i, 9]
                return False
                
        if self.pellets_remaining == 0:
            self.game_over = True
            self.pacman_wins = True
            return True
        return False
    
    def copy(self):
        new_state = GameState()
        new_state.maze = [row[:] for row in self.maze]
        new_state.pacman_pos = self.pacman_pos[:]
        new_state.ghosts = [ghost.copy() for ghost in self.ghosts]
        new_state.score = self.score
        new_state.lives = self.lives
        new_state.level = self.level
        new_state.pellets_remaining = self.pellets_remaining
        new_state.power_pellets_remaining = self.power_pellets_remaining
        new_state.game_over = self.game_over
        new_state.pacman_wins = self.pacman_wins
        new_state.power_mode = self.power_mode
        new_state.power_timer = self.power_timer
        new_state.move_history = self.move_history.copy()
        return new_state

class AdvancedMinimaxAgent:
    def __init__(self, depth=4, use_alpha_beta=True, use_transposition=True):
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.use_transposition = use_transposition
        self.transposition_table = {}
        self.nodes_evaluated = 0
        self.pruning_count = 0
        
    def get_state_hash(self, state):
        """Crea un hash único para el estado del juego"""
        if not self.use_transposition:
            return None
            
        pacman_tuple = tuple(state.pacman_pos)
        ghosts_tuple = tuple(tuple(ghost.pos) for ghost in state.ghosts)
        maze_tuple = tuple(tuple(row) for row in state.maze)
        
        return hash((pacman_tuple, ghosts_tuple, maze_tuple, state.power_mode, state.power_timer))
    
    def evaluate_state(self, state):
        self.nodes_evaluated += 1
        
        if state.is_terminal():
            if state.pacman_wins:
                return 10000 + state.score
            elif state.game_over:
                return -10000
            else:
                return -5000  # Perdió una vida
        
        score = state.score * 10
        
        # Evaluación de distancias a fantasmas
        ghost_penalty = 0
        for ghost in state.ghosts:
            dist = state.manhattan_distance(state.pacman_pos, ghost.pos)
            
            if state.power_mode and ghost.mode == "frightened":
                # En modo poder, acercarse a fantasmas es bueno
                if dist <= 3:
                    score += (4 - dist) * 100
            else:
                # Normalmente, alejarse de fantasmas es bueno
                if dist <= 1:
                    ghost_penalty += 1000
                elif dist <= 2:
                    ghost_penalty += 300
                elif dist <= 3:
                    ghost_penalty += 100
                else:
                    score += min(dist * 5, 50)
        
        score -= ghost_penalty
        
        # Bonus por pellets restantes (menos pellets = mejor)
        total_pellets = state.count_pellets() + state.count_power_pellets()
        pellets_eaten = total_pellets - state.pellets_remaining - state.power_pellets_remaining
        score += pellets_eaten * 50
        
        # Penalizar pellets restantes
        score -= state.pellets_remaining * 5
        
        # Bonus especial por power pellets
        score += (state.count_power_pellets() - state.power_pellets_remaining) * 200
        
        # Bonus por modo poder
        if state.power_mode:
            score += state.power_timer * 20
        
        # Distancia al pellet más cercano
        closest_pellet_dist = self.find_closest_pellet(state)
        if closest_pellet_dist > 0:
            score -= closest_pellet_dist * 3
        
        # Penalizar movimientos repetitivos
        if len(state.move_history) >= 4:
            recent_moves = list(state.move_history)[-4:]
            if len(set(recent_moves)) <= 2:  # Muy pocos movimientos únicos
                score -= 50
        
        # Bonus por exploración (estar en nuevas áreas)
        if state.pacman_pos not in state.move_history:
            score += 30
        
        return score
    
    def find_closest_pellet(self, state):
        min_dist = float('inf')
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if state.maze[y][x] in [1, 3]:
                    dist = state.manhattan_distance(state.pacman_pos, [x, y])
                    min_dist = min(min_dist, dist)
        return min_dist if min_dist != float('inf') else 0
    
    def minimax(self, state, depth, maximizing_player, alpha=float('-inf'), beta=float('inf'), ghost_idx=0):
        state_hash = self.get_state_hash(state)
        if state_hash and state_hash in self.transposition_table:
            cached_depth, cached_value = self.transposition_table[state_hash]
            if cached_depth >= depth:
                return cached_value, None
        
        if depth == 0 or state.is_terminal():
            eval_score = self.evaluate_state(state)
            if state_hash:
                self.transposition_table[state_hash] = (depth, eval_score)
            return eval_score, None
        
        if maximizing_player:
            # Turno de Pacman (MAX)
            max_eval = float('-inf')
            best_move = None
            
            valid_moves = state.get_valid_moves(state.pacman_pos)
            if not valid_moves:
                valid_moves = [Direction.NONE]
            
            # Ordenar movimientos por heurística simple
            def move_priority(move):
                if move == Direction.NONE:
                    return -1000
                dx, dy = move.value
                new_pos = [state.pacman_pos[0] + dx, state.pacman_pos[1] + dy]
                if not state.is_valid_position(new_pos):
                    return -1000
                
                priority = 0
                if state.maze[new_pos[1]][new_pos[0]] == 1:  # Pellet normal
                    priority += 100
                elif state.maze[new_pos[1]][new_pos[0]] == 3:  # Power pellet
                    priority += 500
                
                # Evitar acercarse mucho a fantasmas (excepto en modo poder)
                for ghost in state.ghosts:
                    dist = state.manhattan_distance(new_pos, ghost.pos)
                    if not (state.power_mode and ghost.mode == "frightened"):
                        if dist <= 1:
                            priority -= 1000
                        elif dist <= 2:
                            priority -= 200
                
                return priority
            
            valid_moves.sort(key=move_priority, reverse=True)
            
            for move in valid_moves:
                new_state = state.copy()
                new_state.move_pacman(move)
                new_state.update_power_mode()
                
                eval_score, _ = self.minimax(new_state, depth, False, alpha, beta, 0)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                if self.use_alpha_beta:
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        self.pruning_count += 1
                        break
            
            if state_hash:
                self.transposition_table[state_hash] = (depth, max_eval)
            return max_eval, best_move
        
        else:
            # Turno de los fantasmas (MIN)
            if ghost_idx >= len(state.ghosts):
                # Todos los fantasmas se movieron, siguiente turno de Pacman
                return self.minimax(state, depth - 1, True, alpha, beta, 0)
            
            min_eval = float('inf')
            best_move = None
            
            ghost_moves = state.get_valid_moves(state.ghosts[ghost_idx].pos)
            if not ghost_moves:
                ghost_moves = [Direction.NONE]
            
            for move in ghost_moves:
                new_state = state.copy()
                new_state.move_ghost(ghost_idx, move)
                
                eval_score, _ = self.minimax(new_state, depth, False, alpha, beta, ghost_idx + 1)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                if self.use_alpha_beta:
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        self.pruning_count += 1
                        break
            
            return min_eval, best_move
    
    def get_best_move(self, state):
        self.nodes_evaluated = 0
        self.pruning_count = 0
        start_time = time.time()
        
        _, best_move = self.minimax(state, self.depth, True)
        
        end_time = time.time()
        self.last_think_time = end_time - start_time
        
        return best_move

class SmartGhostAI:
    """IA mejorada para los fantasmas"""
    
    @staticmethod
    def get_ghost_move(ghost, pacman_pos, maze):
        valid_moves = []
        x, y = ghost.pos
        
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            dx, dy = direction.value
            new_pos = [x + dx, y + dy]
            if (0 <= new_pos[0] < MAZE_WIDTH and 0 <= new_pos[1] < MAZE_HEIGHT and 
                maze[new_pos[1]][new_pos[0]] != 0):
                valid_moves.append(direction)
        
        if not valid_moves:
            return Direction.NONE
        
        if ghost.mode == "frightened":
            # Huir de Pacman
            best_move = None
            max_distance = -1
            
            for move in valid_moves:
                dx, dy = move.value
                new_pos = [x + dx, y + dy]
                distance = abs(new_pos[0] - pacman_pos[0]) + abs(new_pos[1] - pacman_pos[1])
                
                if distance > max_distance:
                    max_distance = distance
                    best_move = move
            
            return best_move if best_move else random.choice(valid_moves)
        
        else:
            # Perseguir a Pacman (con algo de aleatoriedad)
            if random.random() < 0.7:  # 70% inteligente
                best_move = None
                min_distance = float('inf')
                
                for move in valid_moves:
                    dx, dy = move.value
                    new_pos = [x + dx, y + dy]
                    distance = abs(new_pos[0] - pacman_pos[0]) + abs(new_pos[1] - pacman_pos[1])
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_move = move
                
                return best_move if best_move else random.choice(valid_moves)
            else:
                # 30% aleatorio
                return random.choice(valid_moves)

class PacmanGame:
    def __init__(self, use_alpha_beta=True, depth=4):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pacman IA Avanzado - Minimax con Optimizaciones")
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        self.state = GameState()
        self.agent = AdvancedMinimaxAgent(depth=depth, use_alpha_beta=use_alpha_beta)
        self.use_alpha_beta = use_alpha_beta
        self.depth = depth
        
        self.move_counter = 0
        self.auto_play = True
        self.game_speed = FPS
        self.paused = False
        
        # Estadísticas
        self.total_games = 0
        self.wins = 0
        self.avg_score = 0
        
    def draw_maze(self):
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if self.state.maze[y][x] == 0:  # Pared
                    pygame.draw.rect(self.screen, COLORS['BLUE'], rect)
                    pygame.draw.rect(self.screen, COLORS['DARK_BLUE'], rect, 2)
                elif self.state.maze[y][x] == 1:  # Pellet
                    pygame.draw.rect(self.screen, COLORS['BLACK'], rect)
                    pygame.draw.circle(self.screen, COLORS['GOLD'], rect.center, 3)
                elif self.state.maze[y][x] == 3:  # Power pellet
                    pygame.draw.rect(self.screen, COLORS['BLACK'], rect)
                    # Efecto parpadeante para power pellets
                    if (pygame.time.get_ticks() // 200) % 2:
                        pygame.draw.circle(self.screen, COLORS['GOLD'], rect.center, 8)
                else:  # Espacio vacío
                    pygame.draw.rect(self.screen, COLORS['BLACK'], rect)
    
    def draw_characters(self):
        # Dibujar Pacman con animación
        pacman_rect = pygame.Rect(
            self.state.pacman_pos[0] * CELL_SIZE + 4,
            self.state.pacman_pos[1] * CELL_SIZE + 4,
            CELL_SIZE - 8, CELL_SIZE - 8
        )
        
        # Efecto de brillo si está en modo poder
        if self.state.power_mode:
            glow_rect = pygame.Rect(
                self.state.pacman_pos[0] * CELL_SIZE + 2,
                self.state.pacman_pos[1] * CELL_SIZE + 2,
                CELL_SIZE - 4, CELL_SIZE - 4
            )
            pygame.draw.ellipse(self.screen, COLORS['WHITE'], glow_rect)
        
        pygame.draw.ellipse(self.screen, COLORS['YELLOW'], pacman_rect)
        
        # Dibujar fantasmas
        for ghost in self.state.ghosts:
            ghost_rect = pygame.Rect(
                ghost.pos[0] * CELL_SIZE + 3,
                ghost.pos[1] * CELL_SIZE + 3,
                CELL_SIZE - 6, CELL_SIZE - 6
            )
            
            if ghost.mode == "frightened":
                # Fantasmas asustados en azul parpadeante
                if (pygame.time.get_ticks() // 150) % 2:
                    color = COLORS['BLUE']
                else:
                    color = COLORS['WHITE']
            else:
                color = ghost.color
            
            pygame.draw.ellipse(self.screen, color, ghost_rect)
            
            # Ojos de fantasma
            eye_size = 3
            left_eye = (ghost.pos[0] * CELL_SIZE + 10, ghost.pos[1] * CELL_SIZE + 10)
            right_eye = (ghost.pos[0] * CELL_SIZE + 22, ghost.pos[1] * CELL_SIZE + 10)
            pygame.draw.circle(self.screen, COLORS['WHITE'], left_eye, eye_size)
            pygame.draw.circle(self.screen, COLORS['WHITE'], right_eye, eye_size)
    
    def draw_info_panel(self):
        # Panel de información lateral
        panel_x = MAZE_WIDTH * CELL_SIZE + 10
        panel_width = 280
        
        # Fondo del panel
        panel_rect = pygame.Rect(panel_x, 0, panel_width, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLORS['GRAY'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['WHITE'], panel_rect, 2)
        
        y_offset = 20
        line_height = 25
        
        # Información del juego
        texts = [
            f"PUNTUACIÓN: {self.state.score}",
            f"VIDAS: {self.state.lives}",
            f"NIVEL: {self.state.level}",
            f"PELLETS: {self.state.pellets_remaining}",
            f"POWER PELLETS: {self.state.power_pellets_remaining}",
            "",
            "ALGORITMO:",
            "Minimax Avanzado" + (" + α-β" if self.use_alpha_beta else ""),
            f"Profundidad: {self.depth}",
            "",
            "ESTADÍSTICAS IA:",
            f"Nodos evaluados: {self.agent.nodes_evaluated}",
            f"Podas α-β: {self.agent.pruning_count}",
            f"Tiempo pensamiento: {getattr(self.agent, 'last_think_time', 0):.3f}s",
            f"Estados en tabla: {len(self.agent.transposition_table)}",
            "",
            "CONTROLES:",
            "ESPACIO: Pausar/Reanudar",
            "R: Reiniciar",
            "+/-: Velocidad",
            "1-5: Profundidad IA",
            "",
            "ESTADÍSTICAS:",
            f"Partidas: {self.total_games}",
            f"Victorias: {self.wins}",
            f"% Éxito: {(self.wins/max(1,self.total_games)*100):.1f}%"
        ]
        
        if self.state.power_mode:
            texts.insert(5, f"MODO PODER: {self.state.power_timer}")
        
        for i, text in enumerate(texts):
            if text == "":
                continue
                
            color = COLORS['WHITE']
            font = self.font_small
            
            if text.startswith(("PUNTUACIÓN", "ALGORITMO", "ESTADÍSTICAS IA", "CONTROLES", "ESTADÍSTICAS")):
                color = COLORS['YELLOW']
                font = self.font_medium
            elif "MODO PODER" in text:
                color = COLORS['GOLD']
                font = self.font_medium
            
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (panel_x + 10, y_offset + i * line_height))
        
        # Estado del juego
        if self.state.game_over:
            if self.state.pacman_wins:
                game_text = self.font_large.render("¡VICTORIA!", True, COLORS['GREEN'])
            else:
                game_text = self.font_large.render("GAME OVER", True, COLORS['RED'])
            
            text_rect = game_text.get_rect(center=(panel_x + panel_width//2, WINDOW_HEIGHT - 100))
            self.screen.blit(game_text, text_rect)
        
        if self.paused:
            pause_text = self.font_large.render("PAUSADO", True, COLORS['PURPLE'])
            text_rect = pause_text.get_rect(center=(panel_x + panel_width//2, WINDOW_HEIGHT - 50))
            self.screen.blit(pause_text, text_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.game_speed = min(20, self.game_speed + 2)
                elif event.key == pygame.K_MINUS:
                    self.game_speed = max(2, self.game_speed - 2)
                elif event.key == pygame.K_1:
                    self.change_depth(1)
                elif event.key == pygame.K_2:
                    self.change_depth(2)
                elif event.key == pygame.K_3:
                    self.change_depth(3)
                elif event.key == pygame.K_4:
                    self.change_depth(4)
                elif event.key == pygame.K_5:
                    self.change_depth(5)
                elif event.key == pygame.K_t:
                    # Toggle transposition table
                    self.agent.use_transposition = not self.agent.use_transposition
                    if not self.agent.use_transposition:
                        self.agent.transposition_table.clear()
                elif event.key == pygame.K_a:
                    # Toggle alpha-beta pruning
                    self.agent.use_alpha_beta = not self.agent.use_alpha_beta
                    self.use_alpha_beta = self.agent.use_alpha_beta
        return True
    
    def change_depth(self, new_depth):
        self.depth = new_depth
        self.agent.depth = new_depth
        self.agent.transposition_table.clear()  # Limpiar tabla al cambiar profundidad
    
    def reset_game(self):
        if self.state.game_over:
            self.total_games += 1
            if self.state.pacman_wins:
                self.wins += 1
        
        self.state = GameState()
        self.agent.transposition_table.clear()
        self.move_counter = 0
        self.paused = False
    
    def move_ghosts_intelligently(self):
        """Movimiento inteligente de fantasmas"""
        for i, ghost in enumerate(self.state.ghosts):
            move = SmartGhostAI.get_ghost_move(ghost, self.state.pacman_pos, self.state.maze)
            self.state.move_ghost(i, move)
    
    def run(self):
        running = True
        
        print("🎮 PACMAN IA AVANZADO")
        print("=" * 50)
        print("🤖 Algoritmo: Minimax con optimizaciones")
        print("🧠 Características:")
        print("   • Poda Alfa-Beta")
        print("   • Tabla de transposición")
        print("   • Función de evaluación avanzada")
        print("   • IA inteligente para fantasmas")
        print("   • Modo poder con estrategia")
        print("\n🎯 Controles:")
        print("   ESPACIO: Pausar/Reanudar")
        print("   R: Reiniciar partida")
        print("   +/-: Cambiar velocidad")
        print("   1-5: Cambiar profundidad IA")
        print("   T: Toggle tabla transposición")
        print("   A: Toggle poda alfa-beta")
        print("\n¡Presiona cualquier tecla para continuar!")
        
        while running:
            if not self.handle_events():
                break
            
            if not self.paused and not self.state.is_terminal():
                # Turno de Pacman con Minimax
                if self.move_counter % 2 == 0:
                    best_move = self.agent.get_best_move(self.state)
                    self.state.move_pacman(best_move)
                else:
                    # Turno de los fantasmas
                    self.move_ghosts_intelligently()
                
                self.state.update_power_mode()
                self.state.is_terminal()
                self.move_counter += 1
            
            # Dibujar todo
            self.screen.fill(COLORS['BLACK'])
            self.draw_maze()
            self.draw_characters()
            self.draw_info_panel()
            
            pygame.display.flip()
            self.clock.tick(self.game_speed)
        
        pygame.quit()
        sys.exit()

def main():
    print("🎮 CONFIGURACIÓN INICIAL")
    print("=" * 30)
    
    # Configuración de profundidad
    while True:
        try:
            depth = int(input("Profundidad del algoritmo (1-6, recomendado 3-4): ") or "3")
            if 1 <= depth <= 6:
                break
            else:
                print("Por favor, ingresa un número entre 1 y 6")
        except ValueError:
            print("Por favor, ingresa un número válido")
    
    # Configuración de poda alfa-beta
    use_alpha_beta = input("¿Usar poda alfa-beta? (S/n): ").lower().strip()
    use_alpha_beta = use_alpha_beta != 'n'
    
    print(f"\n🚀 Iniciando juego...")
    print(f"   Profundidad: {depth}")
    print(f"   Poda α-β: {'Sí' if use_alpha_beta else 'No'}")
    print(f"   Tabla transposición: Sí")
    print(f"   IA fantasmas: Inteligente")
    
    game = PacmanGame(use_alpha_beta=use_alpha_beta, depth=depth)
    game.run()

if __name__ == "__main__":
    main()