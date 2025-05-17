from tkinter import *
from tkinter import messagebox
import numpy as np
import pygame
import os

# Configuration du plateau
size_of_board = 600
symbol_size = (size_of_board / 3 - size_of_board / 10) / 2
symbol_thickness = 50
symbol_X_color = '#EE4035'
symbol_O_color = '#0492CF'
highlight_color = "yellow"
background_color = "white"

class Tic_Tac_Toe():
    def __init__(self):
        # Initialisation de la fenêtre
        self.window = Tk()
        self.window.title('Tic-Tac-Toe Version Assiongbon Aimé KPODAR')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board, bg=background_color)
        self.canvas.pack()

        # Initialisation de pygame pour les sons
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Erreur lors de l'initialisation de pygame.mixer : {e}")

        # Charger les fichiers audio avec vérification
        self.place_sound = self.load_sound("click_sound.mp3")
        self.win_sound = self.load_sound("win_sound.mp3")
        self.error_sound = self.load_sound("error_sound.mp3")

        # Musique de fond (loop)
        if os.path.exists("background_music.mp3"):
            try:
                pygame.mixer.music.load("background_music.mp3")
                pygame.mixer.music.play(-1)  # loop infini
            except Exception as e:
                print(f"Erreur lors du chargement de la musique de fond : {e}")

        # Scores
        self.score_X = 0
        self.score_O = 0
        self.score_X_label = Label(self.window, text=f"Score X: {self.score_X}", font=("Arial", 14), fg=symbol_X_color)
        self.score_X_label.pack(side=LEFT, padx=20)
        self.score_O_label = Label(self.window, text=f"Score O: {self.score_O}", font=("Arial", 14), fg=symbol_O_color)
        self.score_O_label.pack(side=RIGHT, padx=20)

        # Timer
        self.timer_label = Label(self.window, text="Time: 00:00:00", font=("Arial", 14), fg="black")
        self.timer_label.pack(pady=10)

        # Bouton pour rejouer
        self.play_again_button = Button(self.window, text="Play Again", command=self.play_again, font=("Arial", 14))
        self.play_again_button.pack(pady=10)

        # Initialisation du jeu
        self.window.bind('<Button-1>', self.click)
        self.board_status = np.zeros((3, 3))
        self.player_X_turns = True
        self.X_pieces = 0
        self.O_pieces = 0
        self.selected_piece = None
        self.reset_board = False
        self.gameover = False
        self.time_elapsed = 0
        self.initialize_board()
        self.update_timer()

    def load_sound(self, file_name):
        """Charge un fichier audio et gère les erreurs si le fichier est introuvable."""
        if os.path.exists(file_name):
            try:
                return pygame.mixer.Sound(file_name)
            except Exception as e:
                print(f"Erreur lors du chargement du fichier audio '{file_name}' : {e}")
                return None
        else:
            print(f"Erreur : Le fichier '{file_name}' est introuvable.")
            return None

    def initialize_board(self):
        self.canvas.delete("all")
        for i in range(1, 3):
            self.canvas.create_line(0, size_of_board / 3 * i, size_of_board, size_of_board / 3 * i, width=2)
            self.canvas.create_line(size_of_board / 3 * i, 0, size_of_board / 3 * i, size_of_board, width=2)
        self.redraw_pieces()
        if self.selected_piece:
            self.highlight_selected_piece(self.selected_piece)

    def redraw_pieces(self):
        for row in range(3):
            for col in range(3):
                if self.board_status[row][col] == -1:
                    self.draw_X([row, col])
                elif self.board_status[row][col] == 1:
                    self.draw_O([row, col])

    def draw_X(self, logical_position):
        x, y = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_line(x - symbol_size, y - symbol_size, x + symbol_size, y + symbol_size,
                                width=symbol_thickness, fill=symbol_X_color)
        self.canvas.create_line(x + symbol_size, y - symbol_size, x - symbol_size, y + symbol_size,
                                width=symbol_thickness, fill=symbol_X_color)

    def draw_O(self, logical_position):
        x, y = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_oval(x - symbol_size, y - symbol_size, x + symbol_size, y + symbol_size,
                                width=symbol_thickness, outline=symbol_O_color)

    def convert_logical_to_grid_position(self, logical_position):
        return (size_of_board / 3) * logical_position[1] + size_of_board / 6, \
               (size_of_board / 3) * logical_position[0] + size_of_board / 6

    def convert_grid_to_logical_position(self, grid_position):
        return int(grid_position[1] // (size_of_board / 3)), int(grid_position[0] // (size_of_board / 3))

    def play_again(self):
        self.initialize_board()
        self.board_status = np.zeros((3, 3))
        self.X_pieces = 0
        self.O_pieces = 0
        self.player_X_turns = True
        self.selected_piece = None
        self.reset_board = False
        self.gameover = False
        self.time_elapsed = 0
        self.update_timer()
        self.canvas.delete("highlight")

        # Reprendre la musique de fond après une partie
        if os.path.exists("background_music.mp3"):
            pygame.mixer.music.play(-1)

    def update_timer(self):
        if not self.gameover:
            self.time_elapsed += 1
            hours = self.time_elapsed // 3600
            minutes = (self.time_elapsed % 3600) // 60
            seconds = self.time_elapsed % 60
            self.timer_label.config(text=f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.window.after(1000, self.update_timer)

    def is_valid_position(self, pos):
        return 0 <= pos[0] < 3 and 0 <= pos[1] < 3

    def is_grid_occupied(self, pos):
        return self.board_status[pos[0]][pos[1]] != 0

    def is_adjacent(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

    def move_piece(self, from_pos, to_pos, player):
        value = -1 if player == 'X' else 1
        self.board_status[from_pos[0]][from_pos[1]] = 0
        self.board_status[to_pos[0]][to_pos[1]] = value

    def highlight_selected_piece(self, pos):
        x, y = self.convert_logical_to_grid_position(pos)
        self.canvas.create_rectangle(x - symbol_size, y - symbol_size, x + symbol_size, y + symbol_size,
                                     outline=highlight_color, width=4, tags="highlight")

    def is_gameover(self):
        for i in range(3):
            if abs(sum(self.board_status[i, :])) == 3:
                return True
            if abs(sum(self.board_status[:, i])) == 3:
                return True
        diag1 = self.board_status[0, 0] + self.board_status[1, 1] + self.board_status[2, 2]
        diag2 = self.board_status[0, 2] + self.board_status[1, 1] + self.board_status[2, 0]
        if abs(diag1) == 3 or abs(diag2) == 3:
            return True
        return False

    def click(self, event):
        grid_position = [event.x, event.y]
        logical_position = self.convert_grid_to_logical_position(grid_position)

        if not self.is_valid_position(logical_position):
            if self.error_sound:
                self.error_sound.play()
            messagebox.showwarning("Position invalide", "Vous avez cliqué en dehors du plateau.")
            return

        if not self.reset_board:
            if self.player_X_turns:
                self.handle_turn(logical_position, 'X', -1)
            else:
                self.handle_turn(logical_position, 'O', 1)
            if self.is_gameover():
                self.display_gameover()
        else:
            self.play_again()
            self.reset_board = False

    def handle_turn(self, logical_position, player, value):
        pieces = self.X_pieces if player == 'X' else self.O_pieces

        if pieces < 3:
            if not self.is_grid_occupied(logical_position):
                if self.place_sound:
                    self.place_sound.play()
                if player == 'X':
                    self.draw_X(logical_position)
                else:
                    self.draw_O(logical_position)
                self.board_status[logical_position[0]][logical_position[1]] = value
                if player == 'X':
                    self.X_pieces += 1
                else:
                    self.O_pieces += 1
                self.player_X_turns = not self.player_X_turns
                self.selected_piece = None
                self.canvas.delete("highlight")
            else:
                if self.error_sound:
                    self.error_sound.play()
                messagebox.showwarning("Case occupée", "La case est déjà occupée.")
        else:
            if self.selected_piece is None:
                if self.board_status[logical_position[0]][logical_position[1]] == value:
                    self.selected_piece = logical_position
                    self.canvas.delete("highlight")
                    self.highlight_selected_piece(logical_position)
                else:
                    if self.error_sound:
                        self.error_sound.play()
                    messagebox.showwarning("Sélection invalide", "Vous devez sélectionner l'un de vos propres pions.")
            else:
                if logical_position == self.selected_piece:
                    self.selected_piece = None
                    self.canvas.delete("highlight")
                elif self.board_status[logical_position[0]][logical_position[1]] == value:
                    self.selected_piece = logical_position
                    self.canvas.delete("highlight")
                    self.highlight_selected_piece(logical_position)
                else:
                    if not self.is_grid_occupied(logical_position) and self.is_adjacent(self.selected_piece, logical_position):
                        if self.place_sound:
                            self.place_sound.play()
                        self.move_piece(self.selected_piece, logical_position, player)
                        self.selected_piece = None
                        self.player_X_turns = not self.player_X_turns
                        self.initialize_board()
                    else:
                        if self.error_sound:
                            self.error_sound.play()
                        messagebox.showwarning("Déplacement invalide", "La case doit être adjacente et vide.")

    def display_gameover(self):
        pygame.mixer.music.stop()  # stop la musique de fond

        if self.win_sound:
            self.win_sound.play()
            # attend la fin du son avant d’afficher la boîte message
            duration_ms = int(self.win_sound.get_length() * 1000)
            self.window.after(duration_ms, self.show_winner_message)
        else:
            self.show_winner_message()

        self.gameover = True

    def show_winner_message(self):
        if self.player_X_turns:
            winner = 'O'
            self.score_O += 1
        else:
            winner = 'X'
            self.score_X += 1
        messagebox.showinfo("Fin de partie", f"Le joueur {winner} a gagné!")
        self.score_X_label.config(text=f"Score X: {self.score_X}")
        self.score_O_label.config(text=f"Score O: {self.score_O}")
        self.reset_board = True

if __name__ == "__main__":
    game_instance = Tic_Tac_Toe()
    game_instance.window.mainloop()