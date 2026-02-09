"""Chess Troll - Play chess against a bot with troll behaviors."""

from ui import ChessUI


if __name__ == "__main__":
    ui = ChessUI()
    
    try:
        ui.play()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
