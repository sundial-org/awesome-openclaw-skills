#!/usr/bin/env python3
"""
molt.chess helper - Analyze positions and suggest moves.

Usage:
    python play.py --fen "FEN_STRING"
    python play.py --fen "FEN_STRING" --depth 3
    python play.py --game-id 5 --api-key YOUR_KEY
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import chess
except ImportError:
    print("ERROR: python-chess not installed. Run: pip install chess")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None


def load_credentials():
    """Load API key from config file."""
    config_path = Path.home() / ".config" / "molt-chess" / "credentials.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def fetch_game(game_id: int, api_key: str) -> dict:
    """Fetch game state from API."""
    if not requests:
        print("ERROR: requests not installed. Run: pip install requests")
        sys.exit(1)
    
    url = f"https://molt-chess-production.up.railway.app/api/games/{game_id}"
    resp = requests.get(url, headers={"X-API-Key": api_key})
    resp.raise_for_status()
    return resp.json()


def evaluate_position(board: chess.Board) -> float:
    """Simple material-based evaluation."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    
    # Flip for black's perspective
    if board.turn == chess.BLACK:
        score = -score
    
    return score


def analyze_move(board: chess.Board, move: chess.Move) -> dict:
    """Analyze a single move."""
    san = board.san(move)
    
    # Make the move temporarily
    board.push(move)
    
    info = {
        "move": san,
        "uci": move.uci(),
        "is_capture": board.is_capture(move) if hasattr(board, 'is_capture') else False,
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "eval": -evaluate_position(board)  # Negative because we evaluate from opponent's view
    }
    
    board.pop()
    return info


def find_best_moves(fen: str, depth: int = 2, top_n: int = 5) -> list:
    """Find best moves using simple minimax."""
    board = chess.Board(fen)
    
    if board.is_game_over():
        return []
    
    moves_with_eval = []
    
    for move in board.legal_moves:
        board.push(move)
        
        # Simple 1-ply evaluation (just material)
        eval_score = -evaluate_position(board)
        
        # Bonus for checks and captures
        if board.is_check():
            eval_score += 0.5
        if board.is_checkmate():
            eval_score += 100
        
        moves_with_eval.append({
            "move": board.san(move) if hasattr(board, 'san') else move.uci(),
            "uci": move.uci(),
            "eval": eval_score,
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate()
        })
        
        board.pop()
    
    # Sort by eval (higher is better)
    moves_with_eval.sort(key=lambda x: x["eval"], reverse=True)
    
    return moves_with_eval[:top_n]


def main():
    parser = argparse.ArgumentParser(description="molt.chess position analyzer")
    parser.add_argument("--fen", help="FEN string to analyze")
    parser.add_argument("--game-id", type=int, help="Game ID to fetch and analyze")
    parser.add_argument("--api-key", help="API key (or reads from ~/.config/molt-chess/credentials.json)")
    parser.add_argument("--depth", type=int, default=2, help="Search depth (default: 2)")
    parser.add_argument("--top", type=int, default=5, help="Number of moves to show (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Get FEN from args or fetch from API
    if args.game_id:
        api_key = args.api_key or load_credentials().get("api_key")
        if not api_key:
            print("ERROR: --api-key required or set in ~/.config/molt-chess/credentials.json")
            sys.exit(1)
        
        game = fetch_game(args.game_id, api_key)
        fen = game["fen"]
        print(f"Game {args.game_id}: {game.get('white', '?')} vs {game.get('black', '?')}")
        print(f"Turn: {game.get('turn', '?')}")
        print()
    elif args.fen:
        fen = args.fen
    else:
        # Default starting position
        fen = chess.STARTING_FEN
    
    # Analyze
    board = chess.Board(fen)
    
    if board.is_game_over():
        result = board.result()
        print(f"Game over: {result}")
        sys.exit(0)
    
    best_moves = find_best_moves(fen, depth=args.depth, top_n=args.top)
    
    if args.json:
        print(json.dumps({
            "fen": fen,
            "turn": "white" if board.turn == chess.WHITE else "black",
            "best_moves": best_moves
        }, indent=2))
    else:
        print(f"Position: {fen}")
        print(f"Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
        print(f"\nTop {len(best_moves)} moves:")
        print("-" * 40)
        
        for i, m in enumerate(best_moves, 1):
            flags = []
            if m.get("is_checkmate"):
                flags.append("CHECKMATE")
            elif m.get("is_check"):
                flags.append("check")
            
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"{i}. {m['move']:8} (eval: {m['eval']:+.1f}){flag_str}")
        
        print()
        print(f"Recommended: {best_moves[0]['move']}")


if __name__ == "__main__":
    main()
