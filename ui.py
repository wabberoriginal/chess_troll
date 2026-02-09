"""CLI User Interface for Chess Game."""

from typing import Optional
from game import ChessGame


class ChessUI:
    """Command-line interface for chess game."""
    
    def __init__(self):
        self.game = ChessGame()
    
    def display_board(self) -> None:
        """Display the chess board."""
        print("\n" + str(self.game.board) + "\n")
    
    def display_status(self) -> None:
        """Display game status and piece counts."""
        white_captures = ', '.join(str(p) for p in self.game.board.white_captures) if self.game.board.white_captures else "None"
        black_captures = ', '.join(str(p) for p in self.game.board.black_captures) if self.game.board.black_captures else "None"
        
        print(f"White captured: {white_captures}")
        print(f"Black captured: {black_captures}")
        print(f"Bot move count: {self.game.bot.move_count + 1} (next move)")
        print()
    
    def display_game_result(self) -> None:
        """Display game result."""
        if self.game.winner == 'white':
            print("=" * 40)
            print("GAME OVER: WHITE WINS!")
            print("=" * 40)
        elif self.game.winner == 'black':
            print("=" * 40)
            print("GAME OVER: BLACK (BOT) WINS!")
            print("=" * 40)
        else:
            print("=" * 40)
            print("GAME OVER: STALEMATE!")
            print("=" * 40)
    
    def play(self) -> None:
        """Main game loop."""
        print("=" * 40)
        print("CHESS vs BOT")
        print("=" * 40)
        print("You are White. Bot is Black.")
        print("Moves: Standard notation (e.g., e2e4)")
        print("Type 'quit' to exit.")
        print("=" * 40)
        
        self.display_board()
        
        while not self.game.game_over:
            # Player move
            while True:
                self.display_status()
                user_input = input("Your move: ").strip().lower()
                
                if user_input == 'quit':
                    print("Game aborted.")
                    return
                
                if user_input == 'help':
                    legal_moves = self.game.get_legal_moves_notation()
                    print(f"Legal moves: {', '.join(legal_moves)}")
                    continue
                
                success, message = self.game.player_move(user_input)
                print(message)
                
                if success:
                    break
                print()
            
            self.display_board()
            
            if self.game.game_over:
                break
            
            # Bot move
            print("Bot is thinking...")
            success, message = self.game.bot_move()
            print(message)
            
            self.display_board()
        
        self.display_game_result()
        self.display_status()
    
    def play_custom(self) -> None:
        """Play with custom game setup."""
        self.play()
    
    def quit(self) -> None:
        """Quit the game."""
        print("Goodbye!")


def main():
    """Main entry point."""
    ui = ChessUI()
    
    try:
        ui.play()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
