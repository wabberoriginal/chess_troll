"""Chess Troll - Play chess against a bot with troll behaviors."""

import sys

# Try to import GUI, fall back to CLI if GUI not available
try:
    from gui import main as gui_main
    
    if __name__ == "__main__":
        gui_main()
except ImportError:
    print("GUI not available, falling back to CLI mode...")
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
