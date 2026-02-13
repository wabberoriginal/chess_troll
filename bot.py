"""Chess bot AI with minimax algorithm."""

import random
from typing import Optional, List
from board import Board
from moves import Move, MoveGenerator


class ChessBot:
    """Bot player that uses minimax with special move behaviors."""
    
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.move_count = 0  # Counts all moves by black (bot)
    
    def get_move(self, board: Board) -> Optional[Move]:
        """
        Get the next move for black.
        
        Move counting behavior:
        - 5th, 10th, 15th... move: random legal move
        - 4th, 8th, 12th... move: random illegal move
        - Otherwise: minimax best move
        """
        self.move_count += 1
        
        # every 4th move: random illegal move
        if self.move_count % 4 == 0:
            return self._get_random_illegal_move(board)
        
        # 5th move: random legal move
        if self.move_count % 5 == 0:
            return self._get_random_legal_move(board)
        
        # Normal move: minimax
        return self._get_best_move(board)
    
    def _get_best_move(self, board: Board) -> Optional[Move]:
        """Get best move using minimax algorithm."""
        legal_moves = MoveGenerator.get_all_legal_moves(board, 'black')
        
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        best_move = None
        best_score = float('-inf')
        
        for move in legal_moves:
            board_copy = board.copy()
            MoveGenerator.apply_move(board_copy, move)
            score = self._minimax(board_copy, self.depth - 1, False, float('-inf'), float('inf'))
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else legal_moves[0]
    
    def _minimax(self, board: Board, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
        """Minimax with alpha-beta pruning."""
        # Terminal node or depth reached
        if depth == 0:
            return self._evaluate(board)
        
        legal_moves = MoveGenerator.get_all_legal_moves(board, 'black' if is_maximizing else 'white')
        
        # Terminal positions
        if not legal_moves:
            if MoveGenerator.is_checkmate(board, 'black' if is_maximizing else 'white'):
                return 10000 if not is_maximizing else -10000
            else:  # Stalemate
                return 0
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                board_copy = board.copy()
                MoveGenerator.apply_move(board_copy, move)
                eval_score = self._minimax(board_copy, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board_copy = board.copy()
                MoveGenerator.apply_move(board_copy, move)
                eval_score = self._minimax(board_copy, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def _evaluate(self, board: Board) -> float:
        """Evaluate board position for black."""
        score = 0.0
        
        piece_values = {
            'pawn': 1.0,
            'knight': 3.0,
            'bishop': 3.25,
            'rook': 5.0,
            'queen': 9.0,
            'king': 0.0  # King is invaluable
        }
        
        # Material count
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    value = piece_values.get(piece.piece_type, 0.0)
                    if piece.color == 'black':
                        score += value
                    else:
                        score -= value
        
        # Position bonuses
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.piece_type == 'pawn':
                    # Pawn advancement bonus
                    if piece.color == 'black':
                        score += (row - 1) * 0.1
                    else:
                        score -= (6 - row) * 0.1
        
        # Captured pieces influence
        score -= len(board.white_captures) * 0.5
        score += len(board.black_captures) * 0.5
        
        return score
    
    def _get_random_legal_move(self, board: Board) -> Optional[Move]:
        """Get a random legal move."""
        legal_moves = MoveGenerator.get_all_legal_moves(board, 'black')
        return random.choice(legal_moves) if legal_moves else None
    
    def _get_random_illegal_move(self, board: Board) -> Optional[Move]:
        """Get a random illegal move (that stays on board)."""
        illegal_moves = MoveGenerator.get_all_illegal_moves(board)

        if not illegal_moves:
            return None

        # If black king is currently in check, prefer moves that resolve the check.
        # First try legal moves (prefer resolving checks with legal play); otherwise
        # fall back to illegal moves that would resolve the check.
        if MoveGenerator.is_in_check(board, 'black'):
            legal_resolving = []
            legal_moves = MoveGenerator.get_all_legal_moves(board, 'black')
            for m in legal_moves:
                board_copy = board.copy()
                MoveGenerator.apply_move(board_copy, m)
                if not MoveGenerator.is_in_check(board_copy, 'black'):
                    legal_resolving.append(m)

            if legal_resolving:
                return random.choice(legal_resolving)

            # No legal resolving moves; check illegal moves for any that would resolve the check.
            resolving_moves = []
            for m in illegal_moves:
                piece = board.get_piece(m.from_row, m.from_col)
                if not piece or piece.color != 'black':
                    continue
                board_copy = board.copy()
                MoveGenerator.apply_move(board_copy, m)
                if not MoveGenerator.is_in_check(board_copy, 'black'):
                    resolving_moves.append(m)

            if resolving_moves:
                illegal_moves = resolving_moves

        move = random.choice(illegal_moves)

        # Handle pawn promotion for illegal moves
        piece = board.get_piece(move.from_row, move.from_col)
        if piece and piece.piece_type == 'pawn' and piece.color == 'black' and move.to_row == 7:
            # Black pawn reaching white's back rank should promote
            move.promotion_piece = random.choice(['queen', 'rook', 'bishop', 'knight'])

        return move
    
    def reset(self) -> None:
        """Reset move counter."""
        self.move_count = 0
