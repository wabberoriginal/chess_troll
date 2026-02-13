import random
from bot import ChessBot
from board import Board, Piece
from moves import MoveGenerator


def test_illegal_move_resolves_check():
    random.seed(0)

    # Create a minimal board where black king is in check by a white queen.
    board = Board()
    board.squares = [[None for _ in range(8)] for _ in range(8)]

    # Place black king at e8 (row 0, col 4)
    board.set_piece(0, 4, Piece('black', 'king'))
    board.black_king_pos = (0, 4)

    # Place white queen at d7 (row 1, col 3) attacking the king (diagonal)
    board.set_piece(1, 3, Piece('white', 'queen'))

    # Add a black rook for some legal options
    board.set_piece(0, 0, Piece('black', 'rook'))

    bot = ChessBot()
    # Make bot choose the illegal-move branch on get_move (it increments move_count internally)
    bot.move_count = 3

    move = bot.get_move(board)

    assert move is not None, "Bot should return a move"

    # Apply the move to a copy and ensure black is not in check afterwards
    board_copy = board.copy()
    MoveGenerator.apply_move(board_copy, move)

    assert not MoveGenerator.is_in_check(board_copy, 'black'), (
        "After bot's move the black king should no longer be in check"
    )
