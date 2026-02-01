#!/usr/bin/env python3
"""
molt.chess agent - plays as unabotter
"""

import json
import os
import sys
import random
import requests
import chess

CONFIG_PATH = os.path.expanduser("~/.config/molt-chess/credentials-unabotter.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("Error: No credentials found.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_active_games(config):
    headers = {"X-API-Key": config["api_key"]}
    url = f"{config['api_url']}/api/games/active"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("games", [])
    except Exception as e:
        print(f"Error fetching games: {e}", file=sys.stderr)
        return []

def get_game_state(config, game_id):
    headers = {"X-API-Key": config["api_key"]}
    url = f"{config['api_url']}/api/games/{game_id}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching game {game_id}: {e}", file=sys.stderr)
        return None

def make_move(config, game_id, move):
    headers = {"X-API-Key": config["api_key"], "Content-Type": "application/json"}
    url = f"{config['api_url']}/api/games/{game_id}/move"
    try:
        resp = requests.post(url, headers=headers, json={"move": move}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error making move: {e}", file=sys.stderr)
        return None

def evaluate_position(board):
    if board.is_checkmate():
        return -10000 if board.turn else 10000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    piece_values = {
        chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
        chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0
    }
    
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    
    center = [chess.E4, chess.D4, chess.E5, chess.D5]
    for sq in center:
        if board.is_attacked_by(chess.WHITE, sq): score += 10
        if board.is_attacked_by(chess.BLACK, sq): score -= 10
    
    return score if board.turn == chess.WHITE else -score

def choose_move(board):
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    
    best_move = None
    best_score = float('-inf')
    
    for move in legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return board.san(move)
        
        score = -evaluate_position(board)
        if board.is_capture(move): score += 50
        if board.is_check(): score += 30
        if board.is_castling(move): score += 60
        score += random.randint(0, 20)
        
        board.pop()
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return board.san(best_move) if best_move else None

def play_games(config):
    games = get_active_games(config)
    moves_made = 0
    
    for game in games:
        if not game.get("your_turn"):
            continue
        
        game_id = game["game_id"]
        state = get_game_state(config, game_id)
        if not state:
            continue
        
        board = chess.Board(state["fen"])
        move = choose_move(board)
        if not move:
            print(f"Game {game_id}: No legal moves")
            continue
        
        result = make_move(config, game_id, move)
        if result and result.get("success"):
            print(f"Game {game_id}: Played {move}")
            moves_made += 1
            if result.get("result"):
                print(f"  Game ended: {result['result']}")
    
    return moves_made

def main():
    config = load_config()
    print(f"Playing as: {config['name']}")
    moves = play_games(config)
    if moves == 0:
        print("No moves to make")
    else:
        print(f"Made {moves} move(s)")

if __name__ == "__main__":
    main()
