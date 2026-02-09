"""Chess board representation and state management."""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set


@dataclass
class Piece:
    """Represents a chess piece."""
    color: str  # 'white' or 'black'
    piece_type: str  # 'pawn', 'knight', 'bishop', 'rook', 'queen', 'king'
    
    def __repr__(self) -> str:
        return f"{self.color[0].upper()}{self.piece_type[0].upper()}"


@dataclass
class Board:
    """Chess board state."""
    # 8x8 board: board[row][col] where row 0 is rank 8, row 7 is rank 1
    # col 0 is file a, col 7 is file h
    squares: List[List[Optional[Piece]]] = field(default_factory=list)
    white_captures: List[Piece] = field(default_factory=list)
    black_captures: List[Piece] = field(default_factory=list)
    white_king_pos: Tuple[int, int] = (7, 4)  # Starting position
    black_king_pos: Tuple[int, int] = (0, 4)  # Starting position
    en_passant_target: Optional[Tuple[int, int]] = None  # For en passant
    white_can_castle_kingside: bool = True
    white_can_castle_queenside: bool = True
    black_can_castle_kingside: bool = True
    black_can_castle_queenside: bool = True
    halfmove_clock: int = 0  # For 50-move rule
    fullmove_number: int = 1
    
    def __post_init__(self):
        if not self.squares:
            self.initialize_board()
    
    def initialize_board(self) -> None:
        """Set up the standard chess starting position."""
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        
        # Place pawns
        for col in range(8):
            self.squares[1][col] = Piece('black', 'pawn')
            self.squares[6][col] = Piece('white', 'pawn')
        
        # Place back ranks
        back_rank_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col in range(8):
            self.squares[0][col] = Piece('black', back_rank_pieces[col])
            self.squares[7][col] = Piece('white', back_rank_pieces[col])
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.squares[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        """Set piece at position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.squares[row][col] = piece
    
    def position_to_notation(self, row: int, col: int) -> str:
        """Convert board position to chess notation (e.g., 'e4')."""
        return chr(ord('a') + col) + str(8 - row)
    
    def notation_to_position(self, notation: str) -> Optional[Tuple[int, int]]:
        """Convert chess notation to board position."""
        if len(notation) != 2:
            return None
        col = ord(notation[0]) - ord('a')
        row = 8 - int(notation[1])
        if 0 <= col < 8 and 0 <= row < 8:
            return (row, col)
        return None
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board(
            squares=[[piece for piece in row] for row in self.squares],
            white_captures=self.white_captures.copy(),
            black_captures=self.black_captures.copy(),
            white_king_pos=self.white_king_pos,
            black_king_pos=self.black_king_pos,
            en_passant_target=self.en_passant_target,
            white_can_castle_kingside=self.white_can_castle_kingside,
            white_can_castle_queenside=self.white_can_castle_queenside,
            black_can_castle_kingside=self.black_can_castle_kingside,
            black_can_castle_queenside=self.black_can_castle_queenside,
            halfmove_clock=self.halfmove_clock,
            fullmove_number=self.fullmove_number,
        )
        return new_board
    
    def __repr__(self) -> str:
        """Return ASCII representation of board."""
        lines = []
        lines.append("  a b c d e f g h")
        for row in range(8):
            line = str(8 - row) + " "
            for col in range(8):
                piece = self.squares[row][col]
                if piece:
                    piece_chars = {'pawn': 'p', 'knight': 'n', 'bishop': 'b', 
                                   'rook': 'r', 'queen': 'q', 'king': 'k'}
                    char = piece_chars[piece.piece_type]
                    line += char if piece.color == 'black' else char.upper()
                else:
                    line += "."
                line += " "
            line += str(8 - row)
            lines.append(line)
        lines.append("  a b c d e f g h")
        return "\n".join(lines)
