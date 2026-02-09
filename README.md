# Chess Troll

A chess game where you play as White against a mischievous bot that plays Black.

## Features

- **Standard chess rules**: Full chess implementation with legal move validation
- **Minimax bot**: AI opponent thinks 3 moves ahead for normal moves
- **Troll behavior**: 
  - **Every 5th move**: Bot plays a random legal move
  - **Every 7th move**: Bot plays a random illegal move (off-board, into check, etc.)
  - **All other moves**: Bot plays the best move using minimax algorithm

## How to Play

```bash
python main.py
```

### Move Notation

Moves are entered in algebraic notation (e.g., `e2e4` means move piece from e2 to e4).

### Commands

- `e2e4` - Standard move notation
- `help` - Show all legal moves
- `quit` - Exit the game

## Game Features

### Board Representation

- Full 8x8 chess board with accurate piece placement
- Pawn promotion when reaching the back rank
- En passant captures
- Castling (kingside and queenside)

### Piece Handling

- Captured pieces are tracked for each player
- Legal move validation prevents invalid moves
- King movement restricted to safe squares

### Game Endings

- **Checkmate**: When a king is under attack with no legal moves
- **Stalemate**: When the current player has no legal moves (but not in check)
- **Player wins**: Checkmate the bot's king
- **Bot wins**: Checkmate your king

## Project Structure

```
chess_troll/
├── board.py      # Chess board state and piece management
├── moves.py      # Move generation and legal move validation
├── bot.py        # AI with minimax and troll behaviors
├── game.py       # Game flow and orchestration
├── ui.py         # Command-line user interface
└── main.py       # Entry point
```

## Technical Details

### Move Counter

The bot tracks a move counter that increments after each of black's moves:
- **Move count % 5 == 0**: Random legal move
- **Move count % 7 == 0**: Random illegal move
- **Otherwise**: Minimax best move (depth 3)

### Minimax Algorithm

- **Depth**: 3 ply (bot looks ahead 3 moves)
- **Alpha-beta pruning**: For optimization
- **Evaluation function**: Material count, pawn advancement, captured pieces

### Illegal Moves

When the bot makes an illegal move (every 7th move), it's recorded in game history but not applied to the board. This shows the "troll" behavior without breaking the game.