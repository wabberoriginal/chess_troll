"""GUI for Chess Game with Drag and Drop support."""

import tkinter as tk
from tkinter import messagebox, font
from typing import Optional, Tuple
from game import ChessGame
from moves import MoveGenerator


class ChessGUI:
    """Graphical user interface for chess game with drag and drop."""
    
    # Piece Unicode symbols
    PIECE_SYMBOLS = {
        ('white', 'king'): '♔',
        ('white', 'queen'): '♕',
        ('white', 'rook'): '♖',
        ('white', 'bishop'): '♗',
        ('white', 'knight'): '♘',
        ('white', 'pawn'): '♙',
        ('black', 'king'): '♚',
        ('black', 'queen'): '♛',
        ('black', 'rook'): '♜',
        ('black', 'bishop'): '♝',
        ('black', 'knight'): '♞',
        ('black', 'pawn'): '♟',
    }
    
    SQUARE_SIZE = 60
    BOARD_SIZE = SQUARE_SIZE * 8
    LIGHT_SQUARE = '#F0D9B5'
    DARK_SQUARE = '#B58863'
    HIGHLIGHT_COLOR = '#BACA44'
    SELECTED_COLOR = '#7FBF0B'
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Chess vs Bot")
        self.root.resizable(False, False)
        
        self.game = ChessGame()
        self.selected_square: Optional[Tuple[int, int]] = None
        self.legal_moves = []
        self.dragging = False
        self.drag_start: Optional[Tuple[int, int]] = None
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for board
        self.canvas = tk.Canvas(
            main_frame,
            width=self.BOARD_SIZE,
            height=self.BOARD_SIZE,
            bg='gray',
            relief=tk.RAISED,
            bd=2
        )
        self.canvas.pack(side=tk.LEFT, padx=5)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
        self.canvas.bind('<Motion>', self._on_canvas_motion)
        
        # Create right panel
        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, padx=5, fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(
            right_panel,
            text="White to move",
            font=('Arial', 12, 'bold'),
            justify=tk.LEFT,
            wraplength=200
        )
        self.status_label.pack(pady=5)
        
        # Move history
        tk.Label(right_panel, text="Move History:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        self.history_frame = tk.Frame(right_panel)
        self.history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for history
        scrollbar = tk.Scrollbar(self.history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            self.history_frame,
            height=15,
            width=20,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            font=('Courier', 9)
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_text.yview)
        
        # Captured pieces
        tk.Label(right_panel, text="Captured Pieces:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.captures_label = tk.Label(
            right_panel,
            text="White: \nBlack: ",
            font=('Arial', 9),
            justify=tk.LEFT
        )
        self.captures_label.pack(anchor=tk.W, pady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(right_panel)
        buttons_frame.pack(pady=10, fill=tk.X)
        
        tk.Button(buttons_frame, text="New Game", command=self._new_game, width=15).pack(pady=5)
        tk.Button(buttons_frame, text="Undo", command=self._undo_move, width=15).pack(pady=5)
        tk.Button(buttons_frame, text="Quit", command=root.quit, width=15).pack(pady=5)
        
        # Draw initial board
        self.draw_board()
    
    def draw_board(self) -> None:
        """Draw the chess board."""
        self.canvas.delete('all')
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE
                y1 = row * self.SQUARE_SIZE
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                base_color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                
                # Highlight selected square
                if self.selected_square == (row, col):
                    color = self.SELECTED_COLOR
                # Highlight legal moves
                elif any(m.to_row == row and m.to_col == col for m in self.legal_moves):
                    color = self.HIGHLIGHT_COLOR
                else:
                    color = base_color
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')
        
        # Draw coordinates
        for i in range(8):
            # Files (a-h)
            self.canvas.create_text(
                i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                self.BOARD_SIZE - 5,
                text=chr(ord('a') + i),
                font=('Arial', 8),
                fill='black'
            )
            # Ranks (8-1)
            self.canvas.create_text(
                5,
                i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                text=str(8 - i),
                font=('Arial', 8),
                fill='black'
            )
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece:
                    symbol = self.PIECE_SYMBOLS[(piece.color, piece.piece_type)]
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    
                    # Piece color (white pieces are lighter)
                    text_color = 'white' if piece.color == 'white' else 'black'
                    
                    self.canvas.create_text(
                        x, y,
                        text=symbol,
                        font=('Arial', 32),
                        fill=text_color,
                        tags=f'piece_{row}_{col}'
                    )
    
    def _on_canvas_click(self, event) -> None:
        """Handle canvas click."""
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        piece = self.game.board.get_piece(row, col)
        
        # If clicking on a legal move, make the move
        if self.selected_square is not None:
            if any(m.to_row == row and m.to_col == col for m in self.legal_moves):
                self._make_move(self.selected_square, (row, col))
                return
        
        # If clicking on own piece, select it
        if piece and piece.color == 'white':
            self.selected_square = (row, col)
            self._update_legal_moves()
            self.draw_board()
        else:
            self.selected_square = None
            self.legal_moves = []
            self.draw_board()
    
    def _on_canvas_drag(self, event) -> None:
        """Handle canvas drag."""
        if self.selected_square is None:
            return
        
        # Visual feedback during drag (optional - can be enhanced)
        pass
    
    def _on_canvas_motion(self, event) -> None:
        """Handle mouse motion."""
        # Can be used for cursor change or preview
        pass
    
    def _on_canvas_release(self, event) -> None:
        """Handle mouse release for drag and drop."""
        if self.selected_square is None:
            return
        
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        # Check if the target is a legal move
        if any(m.to_row == row and m.to_col == col for m in self.legal_moves):
            self._make_move(self.selected_square, (row, col))
    
    def _update_legal_moves(self) -> None:
        """Update legal moves for selected piece."""
        if self.selected_square is None:
            self.legal_moves = []
            return
        
        row, col = self.selected_square
        piece = self.game.board.get_piece(row, col)
        
        if piece and piece.color == 'white':
            self.legal_moves = MoveGenerator._get_piece_moves(self.game.board, row, col, legal_only=True)
        else:
            self.legal_moves = []
    
    def _make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """Make a move and handle game flow."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Create move notation
        from_notation = chr(ord('a') + from_col) + str(8 - from_row)
        to_notation = chr(ord('a') + to_col) + str(8 - to_row)
        notation = from_notation + to_notation
        
        # Try to make the move
        success, message = self.game.player_move(notation)
        
        if not success:
            messagebox.showwarning("Invalid Move", message)
            self.selected_square = None
            self.legal_moves = []
            self.draw_board()
            return
        
        self.selected_square = None
        self.legal_moves = []
        self._update_display()
        self.draw_board()
        
        # Check if game is over
        if self.game.game_over:
            self._show_game_over()
            return
        
        # Bot move
        self.root.after(500, self._bot_move)
    
    def _bot_move(self) -> None:
        """Execute bot move."""
        self.status_label.config(text="Bot is thinking...")
        self.root.update()
        
        success, message = self.game.bot_move()
        
        self._update_display()
        self.draw_board()
        
        if self.game.game_over:
            self._show_game_over()
    
    def _update_display(self) -> None:
        """Update all display elements."""
        # Update status
        if self.game.game_over:
            if self.game.winner == 'white':
                status = "WHITE WINS!"
            elif self.game.winner == 'black':
                status = "BLACK WINS!"
            else:
                status = "STALEMATE!"
        else:
            status = "White to move"
        
        self.status_label.config(text=status)
        
        # Update move history
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete('1.0', tk.END)
        
        for i, move in enumerate(self.game.move_history, 1):
            move_num = (i + 1) // 2
            if i % 2 == 1:
                self.history_text.insert(tk.END, f"{move_num}. {move} ")
            else:
                self.history_text.insert(tk.END, f"{move}\n")
        
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
        
        # Update captured pieces
        white_captures = ', '.join(str(p) for p in self.game.board.white_captures) if self.game.board.white_captures else "None"
        black_captures = ', '.join(str(p) for p in self.game.board.black_captures) if self.game.board.black_captures else "None"
        
        self.captures_label.config(
            text=f"White: {black_captures}\nBlack: {white_captures}"
        )
    
    def _show_game_over(self) -> None:
        """Show game over dialog."""
        if self.game.winner == 'white':
            message = "Congratulations! You won!"
        elif self.game.winner == 'black':
            message = "Bot wins! Better luck next time."
        else:
            message = "Stalemate! The game is a draw."
        
        messagebox.showinfo("Game Over", message)
    
    def _new_game(self) -> None:
        """Start a new game."""
        if self.game.move_history:
            if not messagebox.askyesno("New Game", "Start a new game?"):
                return
        
        self.game.reset()
        self.selected_square = None
        self.legal_moves = []
        self._update_display()
        self.draw_board()
    
    def _undo_move(self) -> None:
        """Undo the last move (not implemented - would require move reversal)."""
        messagebox.showinfo("Info", "Undo not yet implemented.")


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
