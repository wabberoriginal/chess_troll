"""Chess game orchestration and flow."""

from typing import Optional, Tuple
from board import Board
from moves import Move, MoveGenerator
from bot import ChessBot


class ChessGame:
    """Main chess game controller."""
    
    def __init__(self):
        self.board = Board()
        self.bot = ChessBot(depth=3)
        self.game_over = False
        self.winner = None  # 'white', 'black', 'stalemate'
        self.move_history: list[Move] = []
    
    def get_board_state(self) -> Board:
        """Get current board state."""
        return self.board
    
    def player_move(self, notation: str) -> Tuple[bool, str]:
        """
        Apply player (white) move.
        
        Args:
            notation: Move in standard notation (e.g., 'e2e4')
        
        Returns:
            (success, message)
        """
        # Parse notation
        if len(notation) < 4:
            return False, "Invalid notation. Use format: e2e4"
        
        from_pos = self.board.notation_to_position(notation[:2])
        to_pos = self.board.notation_to_position(notation[2:4])
        
        if not from_pos or not to_pos:
            return False, "Invalid square notation."
        
        # Find matching move
        legal_moves = MoveGenerator.get_all_legal_moves(self.board, 'white')
        matching_move = None
        
        for move in legal_moves:
            if move.from_row == from_pos[0] and move.from_col == from_pos[1] and \
               move.to_row == to_pos[0] and move.to_col == to_pos[1]:
                matching_move = move
                break
        
        if not matching_move:
            return False, "Illegal move."
        
        # Handle promotion
        if matching_move.promotion_piece is None and self.board.get_piece(from_pos[0], from_pos[1]).piece_type == 'pawn':
            if (matching_move.to_row == 0 and self.board.get_piece(from_pos[0], from_pos[1]).color == 'white'):
                return False, "Pawn promotion required. Use notation: e7e8q (q/r/b/n)"
        
        # Apply move
        MoveGenerator.apply_move(self.board, matching_move)
        self.move_history.append(matching_move)
        
        # Check game state after white move
        if MoveGenerator.is_checkmate(self.board, 'black'):
            self.game_over = True
            self.winner = 'white'
            return True, "White wins! Black is in checkmate."
        
        if MoveGenerator.is_stalemate(self.board, 'black'):
            self.game_over = True
            self.winner = 'stalemate'
            return True, "Stalemate!"
        
        return True, "Move accepted."
    
    def bot_move(self) -> Tuple[bool, str]:
        """Apply bot (black) move."""
        move = self.bot.get_move(self.board)
        
        if move is None:
            if MoveGenerator.is_checkmate(self.board, 'black'):
                self.game_over = True
                self.winner = 'white'
                return False, "White wins! Black is in checkmate."
            else:
                self.game_over = True
                self.winner = 'stalemate'
                return False, "Stalemate!"
        
        # Check if move is illegal (7th move behavior)
        legal_moves = MoveGenerator.get_all_legal_moves(self.board, 'black')
        legal_move_set = set((m.from_row, m.from_col, m.to_row, m.to_col) for m in legal_moves)
        move_key = (move.from_row, move.from_col, move.to_row, move.to_col)
        
        if move_key not in legal_move_set:
            # Illegal move - apply it visually but record as illegal
            MoveGenerator.apply_move(self.board, move)
            self.move_history.append(move)
            from_notation = chr(ord('a') + move.from_col) + str(8 - move.from_row)
            to_notation = chr(ord('a') + move.to_col) + str(8 - move.to_row)
            # After applying an illegal move, the move may still produce checkmate/stalemate.
            if MoveGenerator.is_checkmate(self.board, 'white'):
                self.game_over = True
                self.winner = 'black'
                return True, f"Bot plays ILLEGAL move: {from_notation}{to_notation}. Black wins! White is in checkmate."
            if MoveGenerator.is_stalemate(self.board, 'white'):
                self.game_over = True
                self.winner = 'stalemate'
                return True, f"Bot plays ILLEGAL move: {from_notation}{to_notation}. Stalemate!"

            return True, f"Bot plays ILLEGAL move: {from_notation}{to_notation}"
        
        # Apply legal move
        MoveGenerator.apply_move(self.board, move)
        self.move_history.append(move)
        
        from_notation = chr(ord('a') + move.from_col) + str(8 - move.from_row)
        to_notation = chr(ord('a') + move.to_col) + str(8 - move.to_row)
        move_str = f"{from_notation}{to_notation}"
        
        # Check game state after black move
        if MoveGenerator.is_checkmate(self.board, 'white'):
            self.game_over = True
            self.winner = 'black'
            return True, f"Bot plays {move_str}. Black wins! White is in checkmate."
        
        if MoveGenerator.is_stalemate(self.board, 'white'):
            self.game_over = True
            self.winner = 'stalemate'
            return True, f"Bot plays {move_str}. Stalemate!"
        
        return True, f"Bot plays {move_str}."
    
    def reset(self) -> None:
        """Reset the game."""
        self.board = Board()
        self.bot.reset()
        self.game_over = False
        self.winner = None
        self.move_history = []
    
    def get_legal_moves_notation(self) -> list[str]:
        """Get all legal moves in notation format."""
        legal_moves = MoveGenerator.get_all_legal_moves(self.board, 'white')
        return [str(move) for move in legal_moves]
