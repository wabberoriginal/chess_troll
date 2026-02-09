"""Chess move generation and validation."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from board import Board, Piece


@dataclass
class Move:
    """Represents a chess move."""
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    is_capture: bool = False
    captured_piece: Optional[Piece] = None
    promotion_piece: Optional[str] = None
    is_castling: bool = False
    is_en_passant: bool = False
    
    def __repr__(self) -> str:
        from_notation = chr(ord('a') + self.from_col) + str(8 - self.from_row)
        to_notation = chr(ord('a') + self.to_col) + str(8 - self.to_row)
        return f"{from_notation}{to_notation}"


class MoveGenerator:
    """Generates legal and illegal moves."""
    
    @staticmethod
    def get_all_legal_moves(board: Board, color: str) -> List[Move]:
        """Get all legal moves for a color."""
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == color:
                    moves.extend(MoveGenerator._get_piece_moves(board, row, col, legal_only=True))
        
        return moves
    
    @staticmethod
    def _get_piece_moves(board: Board, row: int, col: int, legal_only: bool = True) -> List[Move]:
        """Get all moves (legal or pseudo-legal) for a piece."""
        piece = board.get_piece(row, col)
        if not piece:
            return []
        
        moves = []
        
        if piece.piece_type == 'pawn':
            moves = MoveGenerator._get_pawn_moves(board, row, col)
        elif piece.piece_type == 'knight':
            moves = MoveGenerator._get_knight_moves(board, row, col, piece.color)
        elif piece.piece_type == 'bishop':
            moves = MoveGenerator._get_sliding_moves(board, row, col, piece.color, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
        elif piece.piece_type == 'rook':
            moves = MoveGenerator._get_sliding_moves(board, row, col, piece.color, [(0, 1), (0, -1), (1, 0), (-1, 0)])
        elif piece.piece_type == 'queen':
            moves = MoveGenerator._get_sliding_moves(board, row, col, piece.color, 
                                                    [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)])
        elif piece.piece_type == 'king':
            moves = MoveGenerator._get_king_moves(board, row, col, piece.color)
        
        if legal_only:
            # Filter out moves that leave king in check
            legal_moves = []
            for move in moves:
                board_copy = board.copy()
                MoveGenerator.apply_move(board_copy, move)
                if not MoveGenerator.is_in_check(board_copy, piece.color):
                    legal_moves.append(move)
            return legal_moves
        
        return moves
    
    @staticmethod
    def _get_pawn_moves(board: Board, row: int, col: int) -> List[Move]:
        """Get pawn moves."""
        moves = []
        piece = board.get_piece(row, col)
        direction = -1 if piece.color == 'white' else 1
        start_row = 6 if piece.color == 'white' else 1
        promotion_row = 0 if piece.color == 'white' else 7
        
        # Forward move
        forward_row = row + direction
        if 0 <= forward_row < 8:
            if board.get_piece(forward_row, col) is None:
                move = Move(row, col, forward_row, col)
                if forward_row == promotion_row:
                    for promo in ['queen', 'rook', 'bishop', 'knight']:
                        move_promo = Move(row, col, forward_row, col, promotion_piece=promo)
                        moves.append(move_promo)
                else:
                    moves.append(move)
                
                # Double move from start
                if row == start_row:
                    double_row = row + 2 * direction
                    if board.get_piece(double_row, col) is None:
                        moves.append(Move(row, col, double_row, col))
        
        # Captures (including en passant)
        for capture_col in [col - 1, col + 1]:
            if 0 <= capture_col < 8:
                capture_row = row + direction
                if 0 <= capture_row < 8:
                    target_piece = board.get_piece(capture_row, capture_col)
                    if target_piece and target_piece.color != piece.color:
                        move = Move(row, col, capture_row, capture_col, is_capture=True, captured_piece=target_piece)
                        if capture_row == promotion_row:
                            for promo in ['queen', 'rook', 'bishop', 'knight']:
                                move_promo = Move(row, col, capture_row, capture_col, is_capture=True, 
                                                captured_piece=target_piece, promotion_piece=promo)
                                moves.append(move_promo)
                        else:
                            moves.append(move)
                    # En passant
                    elif board.en_passant_target == (capture_row, capture_col):
                        en_passant_move = Move(row, col, capture_row, capture_col, is_capture=True, 
                                             captured_piece=board.get_piece(row, capture_col), is_en_passant=True)
                        moves.append(en_passant_move)
        
        return moves
    
    @staticmethod
    def _get_knight_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
        """Get knight moves."""
        moves = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece(new_row, new_col)
                if target is None or target.color != color:
                    is_capture = target is not None
                    moves.append(Move(row, col, new_row, new_col, is_capture=is_capture, captured_piece=target))
        
        return moves
    
    @staticmethod
    def _get_sliding_moves(board: Board, row: int, col: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
        """Get sliding moves (bishop, rook, queen)."""
        moves = []
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append(Move(row, col, new_row, new_col))
                elif target.color != color:
                    moves.append(Move(row, col, new_row, new_col, is_capture=True, captured_piece=target))
                    break
                else:
                    break
                new_row += dr
                new_col += dc
        
        return moves
    
    @staticmethod
    def _get_king_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
        """Get king moves including castling."""
        moves = []
        
        # Regular king moves
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = board.get_piece(new_row, new_col)
                    if target is None or target.color != color:
                        is_capture = target is not None
                        moves.append(Move(row, col, new_row, new_col, is_capture=is_capture, captured_piece=target))
        
        # Castling (pseudo-legal, legality checked later)
        if color == 'white':
            if board.white_can_castle_kingside:
                if board.get_piece(7, 5) is None and board.get_piece(7, 6) is None:
                    moves.append(Move(7, 4, 7, 6, is_castling=True))
            if board.white_can_castle_queenside:
                if board.get_piece(7, 1) is None and board.get_piece(7, 2) is None and board.get_piece(7, 3) is None:
                    moves.append(Move(7, 4, 7, 2, is_castling=True))
        else:
            if board.black_can_castle_kingside:
                if board.get_piece(0, 5) is None and board.get_piece(0, 6) is None:
                    moves.append(Move(0, 4, 0, 6, is_castling=True))
            if board.black_can_castle_queenside:
                if board.get_piece(0, 1) is None and board.get_piece(0, 2) is None and board.get_piece(0, 3) is None:
                    moves.append(Move(0, 4, 0, 2, is_castling=True))
        
        return moves
    
    @staticmethod
    def apply_move(board: Board, move: Move) -> None:
        """Apply a move to the board."""
        piece = board.get_piece(move.from_row, move.from_col)
        
        # Handle captures
        if move.is_capture and move.captured_piece:
            if piece.color == 'white':
                board.black_captures.append(move.captured_piece)
            else:
                board.white_captures.append(move.captured_piece)
            board.set_piece(move.to_row, move.to_col, None)
        
        # Handle en passant
        if move.is_en_passant:
            ep_piece = board.get_piece(move.from_row, move.to_col)
            if piece.color == 'white':
                board.black_captures.append(ep_piece)
            else:
                board.white_captures.append(ep_piece)
            board.set_piece(move.from_row, move.to_col, None)
        
        # Move the piece
        new_piece = piece
        if move.promotion_piece:
            new_piece = Piece(piece.color, move.promotion_piece)
        
        board.set_piece(move.from_row, move.from_col, None)
        board.set_piece(move.to_row, move.to_col, new_piece)
        
        # Update king position
        if piece.piece_type == 'king':
            if piece.color == 'white':
                board.white_king_pos = (move.to_row, move.to_col)
            else:
                board.black_king_pos = (move.to_row, move.to_col)
        
        # Handle castling
        if move.is_castling:
            if piece.color == 'white':
                if move.to_col == 6:  # Kingside
                    rook = board.get_piece(7, 7)
                    board.set_piece(7, 7, None)
                    board.set_piece(7, 5, rook)
                else:  # Queenside
                    rook = board.get_piece(7, 0)
                    board.set_piece(7, 0, None)
                    board.set_piece(7, 3, rook)
            else:
                if move.to_col == 6:  # Kingside
                    rook = board.get_piece(0, 7)
                    board.set_piece(0, 7, None)
                    board.set_piece(0, 5, rook)
                else:  # Queenside
                    rook = board.get_piece(0, 0)
                    board.set_piece(0, 0, None)
                    board.set_piece(0, 3, rook)
        
        # Update castling rights
        if piece.piece_type == 'king':
            if piece.color == 'white':
                board.white_can_castle_kingside = False
                board.white_can_castle_queenside = False
            else:
                board.black_can_castle_kingside = False
                board.black_can_castle_queenside = False
        elif piece.piece_type == 'rook':
            if piece.color == 'white':
                if move.from_col == 0:
                    board.white_can_castle_queenside = False
                elif move.from_col == 7:
                    board.white_can_castle_kingside = False
            else:
                if move.from_col == 0:
                    board.black_can_castle_queenside = False
                elif move.from_col == 7:
                    board.black_can_castle_kingside = False
        
        # Update en passant target
        if piece.piece_type == 'pawn' and abs(move.to_row - move.from_row) == 2:
            board.en_passant_target = (move.from_row + (move.to_row - move.from_row) // 2, move.to_col)
        else:
            board.en_passant_target = None
        
        # Update halfmove clock
        if piece.piece_type == 'pawn' or move.is_capture:
            board.halfmove_clock = 0
        else:
            board.halfmove_clock += 1
    
    @staticmethod
    def is_in_check(board: Board, color: str) -> bool:
        """Check if a color is in check."""
        king_pos = board.white_king_pos if color == 'white' else board.black_king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check if any opponent piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == opponent_color:
                    pseudo_legal_moves = MoveGenerator._get_piece_moves(board, row, col, legal_only=False)
                    for move in pseudo_legal_moves:
                        if move.to_row == king_pos[0] and move.to_col == king_pos[1]:
                            return True
        return False
    
    @staticmethod
    def is_checkmate(board: Board, color: str) -> bool:
        """Check if a color is in checkmate."""
        if not MoveGenerator.is_in_check(board, color):
            return False
        return len(MoveGenerator.get_all_legal_moves(board, color)) == 0
    
    @staticmethod
    def is_stalemate(board: Board, color: str) -> bool:
        """Check if a color is in stalemate."""
        if MoveGenerator.is_in_check(board, color):
            return False
        return len(MoveGenerator.get_all_legal_moves(board, color)) == 0
    
    @staticmethod
    def get_all_illegal_moves(board: Board) -> List[Move]:
        """Get all illegal moves that stay on the board (moves that violate chess rules)."""
        illegal_moves = []
        legal_moves_black = MoveGenerator.get_all_legal_moves(board, 'black')
        legal_moves_set = set((m.from_row, m.from_col, m.to_row, m.to_col) for m in legal_moves_black)
        
        # 1. Try moving black pieces to all possible squares (including illegal ones like into check)
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == 'black':
                    # Try moving to every other square on the board
                    for to_row in range(8):
                        for to_col in range(8):
                            # Skip if it's the same square
                            if to_row == row and to_col == col:
                                continue
                            
                            move_key = (row, col, to_row, to_col)
                            # Only add if it's not a legal move
                            if move_key not in legal_moves_set:
                                move = Move(row, col, to_row, to_col)
                                # Check if target is occupied by opponent or own piece
                                target = board.get_piece(to_row, to_col)
                                if target:
                                    if target.color != 'black':
                                        move.is_capture = True
                                        move.captured_piece = target
                                illegal_moves.append(move)
        
        # 2. Add moves of white pieces (moving opponent's pieces is illegal)
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == 'white':
                    # Try moving white pieces to all possible squares
                    for to_row in range(8):
                        for to_col in range(8):
                            if to_row == row and to_col == col:
                                continue
                            
                            move = Move(row, col, to_row, to_col)
                            target = board.get_piece(to_row, to_col)
                            if target:
                                if target.color != 'white':
                                    move.is_capture = True
                                    move.captured_piece = target
                            illegal_moves.append(move)
        
        return illegal_moves
