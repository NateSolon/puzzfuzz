import chess
import requests
import pandas as pd
import time


base_url = "https://explorer.lichess.ovh/lichess"
speeds = "blitz,rapid,classical"


def add_real_game_data(puzzles):
    best_counts, other_counts = [], []
    i = 0
    for fen, moves in zip(puzzles["FEN"], puzzles["Moves"]):
        i += 1
        if i % 10 == 0:
            print(i)
        best, other = get_game_data(fen, moves)
        best_counts.append(best)
        other_counts.append(other)

    puzzles["Best"] = best_counts
    puzzles["Other"] = other_counts
    puzzles["Total"] = puzzles["Best"] + puzzles["Other"]
    return puzzles


def puzzfuzz(df):
    """
    Filter for enough occurrences and calculate PuzzFuzz metric.
    """
    df["Pct"] = df["Best"] / (df["Best"] + df["Other"])
    df["PuzzFuzz"] = df["Pct"] * df["Rating"]
    df = df.sort_values("PuzzFuzz")
    return df


def get_game_data(fen, moves):
    """
    Get real game data given a puzzle position and solution.
    """
    moves = moves.split()
    board = chess.Board(fen)
    board.push_uci(
        moves[0]
    )  # Lichess puzzles contain the opponent's first move, so we go to the next move
    explorer_data = get_position_data(board.fen())
    best_move = moves[1]
    best, other = get_stats(best_move, explorer_data)
    return best, other


def get_position_data(fen):
    """
    Get the opening explorer data for a position.
    """
    time.sleep(1)
    r = requests.get(base_url, params={"fen": fen, "speeds": speeds})
    if r.status_code == 429:
        print("RATE LIMITED")
        time.sleep(60)
        r = requests.get(base_url, params={"fen": fen, "speeds": speeds})
    data = r.json()
    move_data = data["moves"]
    return move_data


def get_stats(best_move, explorer_data):
    """
    Get how often the best move was played and how often all other moves were played.
    """
    best = 0
    other = 0
    for move in explorer_data:
        num_games = move["white"] + move["black"] + move["draws"]
        if move["uci"] == best_move:
            best += num_games
        else:
            other += num_games
    return best, other
