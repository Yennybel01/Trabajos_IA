import tkinter as tk
from tkinter import messagebox
import math

class TicTacToeGame:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'  # X = Jugador, O = IA
        
    def print_board(self):
        """Imprime el tablero en consola"""
        print("\nTablero actual:")
        print(" {} | {} | {} ".format(self.board[0], self.board[1], self.board[2]))
        print("-----------")
        print(" {} | {} | {} ".format(self.board[3], self.board[4], self.board[5]))
        print("-----------")
        print(" {} | {} | {} ".format(self.board[6], self.board[7], self.board[8]))
        print("\nPosiciones:")
        print(" 0 | 1 | 2 ")
        print("-----------")
        print(" 3 | 4 | 5 ")
        print("-----------")
        print(" 6 | 7 | 8 ")
    
    def is_winner(self, board, player):
        """Verifica si un jugador ha ganado"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columnas
            [0, 4, 8], [2, 4, 6]              # diagonales
        ]
        
        for pattern in win_patterns:
            if all(board[i] == player for i in pattern):
                return True
        return False
    
    def is_board_full(self, board):
        """Verifica si el tablero está lleno"""
        return ' ' not in board
    
    def get_available_moves(self, board):
        """Obtiene las posiciones disponibles"""
        return [i for i, spot in enumerate(board) if spot == ' ']
    
    def minimax(self, board, depth, is_maximizing):
        """
        Algoritmo Minimax
        - is_maximizing = True: turno de la IA (maximizar)
        - is_maximizing = False: turno del jugador (minimizar)
        """
        
        if self.is_winner(board, 'O'):  
            return 10 - depth
        if self.is_winner(board, 'X'):  
            return depth - 10
        if self.is_board_full(board): 
            return 0
        
        if is_maximizing:
            max_eval = -math.inf
            for move in self.get_available_moves(board):
                board[move] = 'O'
                eval_score = self.minimax(board, depth + 1, False)
                board[move] = ' ' 
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = math.inf
            for move in self.get_available_moves(board):
                board[move] = 'X'
                eval_score = self.minimax(board, depth + 1, True)
                board[move] = ' '  #
                min_eval = min(min_eval, eval_score)
            return min_eval
    
    def get_best_move(self):
        """Encuentra el mejor movimiento para la IA usando minimax"""
        best_move = -1
        best_value = -math.inf
        
        print("IA analizando movimientos...")
        
        for move in self.get_available_moves(self.board):
            self.board[move] = 'O'
            move_value = self.minimax(self.board, 0, False)
            self.board[move] = ' '  # deshacer movimiento
            
            print(f"Posición {move}: Valor = {move_value}")
            
            if move_value > best_value:
                best_value = move_value
                best_move = move
        
        print(f"IA elige posición {best_move} con valor {best_value}")
        return best_move
    
    def make_move(self, position, player):
        """Realiza un movimiento"""
        if self.board[position] == ' ':
            self.board[position] = player
            return True
        return False
    
    def play_console_game(self):
        """Juego por consola"""
        print("=== TRES EN RAYA CON MINIMAX ===")
        print("Tú eres X, la IA es O")
        
        while True:
            self.print_board()
            
            # Turno del jugador
            if self.current_player == 'X':
                try:
                    move = int(input("\nIngresa tu movimiento (0-8): "))
                    if move < 0 or move > 8:
                        print("Posición inválida. Usa números del 0 al 8.")
                        continue
                    if not self.make_move(move, 'X'):
                        print("Esa posición ya está ocupada.")
                        continue
                except ValueError:
                    print("Por favor ingresa un número válido.")
                    continue
            
            # Turno de la IA
            else:
                ai_move = self.get_best_move()
                self.make_move(ai_move, 'O')
                print(f"\nIA juega en posición {ai_move}")
            
            # Verificar ganador
            if self.is_winner(self.board, self.current_player):
                self.print_board()
                if self.current_player == 'X':
                    print("\n🎉 ¡Felicidades! ¡Has ganado!")
                else:
                    print("\n🤖 La IA ha ganado. ¡Inténtalo de nuevo!")
                break
            
            # Verificar empate
            if self.is_board_full(self.board):
                self.print_board()
                print("\n🤝 ¡Empate! Buen juego.")
                break
            
            # Cambiar turno
            self.current_player = 'O' if self.current_player == 'X' else 'X'

class TicTacToeGUI:
    def __init__(self):
        self.game = TicTacToeGame()
        self.root = tk.Tk()
        self.root.title("Tres en Raya - Minimax")
        self.root.geometry("400x500")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.buttons = []
        self.player_score = 0
        self.ai_score = 0
        self.draws = 0
        
        self.setup_gui()
    
    def setup_gui(self):
        """Configura la interfaz gráfica"""
        # Título
        title_label = tk.Label(
            self.root, 
            text="TRES EN RAYA", 
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # Estado del juego
        self.status_label = tk.Label(
            self.root,
            text="Tu turno (X)",
            font=('Arial', 12),
            fg='#3498db',
            bg='#2c3e50'
        )
        self.status_label.pack(pady=5)
        
        # Frame del tablero
        board_frame = tk.Frame(self.root, bg='#34495e')
        board_frame.pack(pady=20)
        
        # Crear botones del tablero
        for i in range(9):
            btn = tk.Button(
                board_frame,
                text=' ',
                font=('Arial', 20, 'bold'),
                width=3,
                height=1,
                command=lambda idx=i: self.player_move(idx),
                bg='white',
                fg='black',
                relief='raised',
                bd=3
            )
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)
        
        # Marcador
        score_frame = tk.Frame(self.root, bg='#2c3e50')
        score_frame.pack(pady=20)
        
        self.score_label = tk.Label(
            score_frame,
            text=f"Jugador: {self.player_score} | Empates: {self.draws} | IA: {self.ai_score}",
            font=('Arial', 12),
            fg='white',
            bg='#2c3e50'
        )
        self.score_label.pack()
        
        # Botones de control
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=10)
        
        new_game_btn = tk.Button(
            control_frame,
            text="Nuevo Juego",
            font=('Arial', 12),
            command=self.new_game,
            bg='#27ae60',
            fg='white',
            relief='raised',
            bd=2
        )
        new_game_btn.pack(side=tk.LEFT, padx=5)
        
        reset_score_btn = tk.Button(
            control_frame,
            text="Reiniciar Marcador",
            font=('Arial', 12),
            command=self.reset_scores,
            bg='#e74c3c',
            fg='white',
            relief='raised',
            bd=2
        )
        reset_score_btn.pack(side=tk.LEFT, padx=5)
        
        # Información del algoritmo
        info_label = tk.Label(
            self.root,
            text="La IA usa el algoritmo Minimax\n¡Es imposible ganarle!",
            font=('Arial', 10),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        info_label.pack(pady=10)
    
    def player_move(self, position):
        """Maneja el movimiento del jugador"""
        if self.game.board[position] != ' ' or self.game.current_player != 'X':
            return
        
        # Realizar movimiento del jugador
        self.game.make_move(position, 'X')
        self.buttons[position].config(text='X', fg='#3498db', state='disabled')
        
        # Verificar si el jugador ganó
        if self.game.is_winner(self.game.board, 'X'):
            self.status_label.config(text="¡Ganaste! 🎉", fg='#27ae60')
            self.player_score += 1
            self.disable_all_buttons()
            self.update_score()
            return
        
        # Verificar empate
        if self.game.is_board_full(self.game.board):
            self.status_label.config(text="¡Empate! 🤝", fg='#f39c12')
            self.draws += 1
            self.update_score()
            return
        
        # Turno de la IA
        self.status_label.config(text="IA pensando...", fg='#e74c3c')
        self.root.update()
        self.root.after(500, self.ai_move)  # Delay para efecto visual
    
    def ai_move(self):
        """Maneja el movimiento de la IA"""
        ai_position = self.game.get_best_move()
        self.game.make_move(ai_position, 'O')
        self.buttons[ai_position].config(text='O', fg='#e74c3c', state='disabled')
        
        # Verificar si la IA ganó
        if self.game.is_winner(self.game.board, 'O'):
            self.status_label.config(text="IA gana 🤖", fg='#e74c3c')
            self.ai_score += 1
            self.disable_all_buttons()
            self.update_score()
            return
        
        # Verificar empate
        if self.game.is_board_full(self.game.board):
            self.status_label.config(text="¡Empate! 🤝", fg='#f39c12')
            self.draws += 1
            self.update_score()
            return
        
        # Continuar juego
        self.status_label.config(text="Tu turno (X)", fg='#3498db')
    
    def disable_all_buttons(self):
        """Deshabilita todos los botones"""
        for btn in self.buttons:
            btn.config(state='disabled')
    
    def new_game(self):
        """Inicia un nuevo juego"""
        self.game = TicTacToeGame()
        for btn in self.buttons:
            btn.config(text=' ', state='normal', fg='black')
        self.status_label.config(text="Tu turno (X)", fg='#3498db')
    
    def reset_scores(self):
        """Reinicia el marcador"""
        self.player_score = 0
        self.ai_score = 0
        self.draws = 0
        self.update_score()
    
    def update_score(self):
        """Actualiza el marcador"""
        self.score_label.config(
            text=f"Jugador: {self.player_score} | Empates: {self.draws} | IA: {self.ai_score}"
        )
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

def main():
    print("¿Cómo quieres jugar?")
    print("1. Consola")
    print("2. Interfaz gráfica")
    
    choice = input("Elige una opción (1 o 2): ")
    
    if choice == '1':
        game = TicTacToeGame()
        game.play_console_game()
    elif choice == '2':
        gui = TicTacToeGUI()
        gui.run()
    else:
        print("Opción no válida. Ejecutando interfaz gráfica...")
        gui = TicTacToeGUI()
        gui.run()

if __name__ == "__main__":
    main()