import pandas as pd
import requests

cols = "PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl".split(",")



def download_puzzle_db(to="data/lichess_db_puzzle.csv.bz2"):
    """
    Download the puzzle database from Lichess.
    """
    data = requests.get("https://database.lichess.org/lichess_db_puzzle.csv.bz2")
    with open(to, "wb") as f:
        f.write(data.content)


def process_puzzle_db(
    puzzle_db="data/lichess_db_puzzle.csv.bz2",
    out="data/opening_puzzles.csv",
    move_number=10,
    n=100,
):
    """
    Create move number column and filter puzzles.
    """
    df = pd.read_csv(puzzle_db, names=cols, compression="bz2")
    df["MoveNum"] = df["FEN"].apply(lambda fen: int(fen.split()[-1]))
    df = df[(df["MoveNum"] <= move_number) & (df["NbPlays"] >= n)]
    return df
