"""
Using the search and score funtions from search_and_score.py we make two bots compete here now! :D
Each bot will have it's own set of weights, and they will simply pick the highest scoring move each turn (random if it's a tie)

We will also need to keep track of who wins, for later use in the GA
"""

import chess
import random
from search_and_score import build_search_tree, score_tree


def play_game(weights_1:dict, weights_2:dict, search_depth:int=1, replayable:bool=False) -> tuple:
    """
    Plays a game, using the weights for the scoring of each bot's descisions
    Returns bool-like value for winner, if bot_1 wins we return 0, bot_2 wins we return 1, and on a tie we return 2

    We simply pick the highest score, and random between them during ties
    """
    board = chess.Board()
    moves_made = [] # For replay later

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            weights = weights_1
            is_white = True
        else:
            weights = weights_2
            is_white = False

        tree = build_search_tree(board, depth=search_depth)
        scored_moves = score_tree(tree, is_player_white=is_white, weights=weights)

        move_scores = {}
        max_score = 0
        for move, subtree in scored_moves.items():
            if type(subtree) is dict:
                move_scores[move] = subtree["score"]
            else:
                max_score = subtree
        best_moves = [move for move, score in move_scores.items() if score == max_score]

        chosen_move = random.choice(best_moves)
        moves_made.append(chosen_move)

        #print(chosen_move)

        move = chess.Move.from_uci(chosen_move)
        board.push(move)

    result = board.result()
    if result == "1-0":
        return (0, moves_made) if replayable else (0,)
    elif result == "0-1":
        return (1, moves_made) if replayable else (1,)
    else:
        return (2, moves_made) if replayable else (2,) # Tie case

    
def view_replay(moves:list):
    """
    Given a list of moves, replay the game in the console, and into a txt file (result.txt)
    """
    board = chess.Board()
    with open("result.txt", "w") as f:
        f.write("Initial Board:\n")
        f.write(str(board) + "\n\n")
        print("Initial Board:")
        print(board)
        print()

        for move in moves:
            board_move = chess.Move.from_uci(move)
            board.push(board_move)
            f.write(str(board) + "\n\n")
            print(board)
            print()


if __name__ == "__main__":
    import time

    weights_bot1={
        "friendly_pawn_count": 2,
        "friendly_knight_count": 2,
        "friendly_bishop_count": 2,
        "friendly_rook_count": 2,
        "friendly_queen_count": 2,
        "friendly_king_count": 2,
        "enemy_pawn_count": 1,
        "enemy_knight_count": 1,
        "enemy_bishop_count": 1,
        "enemy_rook_count": 1,
        "enemy_queen_count": 1,
        "enemy_king_count": 1,
        "we_have_more": 2,
        "friendly_protected_pieces": 2,
        "friendly_in_check": 1,
        "enemy_in_check": 1,
        "friendly_in_checkmate": 2,
        "enemy_in_checkmate": 1,
        "enemy_proximity_to_friendly_king": 1,
        "friendly_proximity_to_enemy_king": 3,
        "friendly_center_control": 1,
        "enemy_center_control": 1,
        "friendly_threatening_unprotected": 1,
        "enemy_threatening_unprotected": 1,
        "friendly_pawn_promotion_distance": 1,
        "enemy_pawn_promotion_distance": 1,
        "can_castle": 1,
        "can_en_passant": 1,
        "num_legal_moves": 1
    }

    weights_bot2={
        "friendly_pawn_count": 1,
        "friendly_knight_count": 1,
        "friendly_bishop_count": 1,
        "friendly_rook_count": 1,
        "friendly_queen_count": 1,
        "friendly_king_count": 1,
        "enemy_pawn_count": 1,
        "enemy_knight_count": 1,
        "enemy_bishop_count": 1,
        "enemy_rook_count": 1,
        "enemy_queen_count": 1,
        "enemy_king_count": 1,
        "we_have_more": 1,
        "friendly_protected_pieces": 3,
        "friendly_in_check": 1,
        "enemy_in_check": 10,
        "friendly_in_checkmate": 1,
        "enemy_in_checkmate": 1,
        "enemy_proximity_to_friendly_king": 2,
        "friendly_proximity_to_enemy_king": 3,
        "friendly_center_control": 2,
        "enemy_center_control": 1,
        "friendly_threatening_unprotected": 2,
        "enemy_threatening_unprotected": 1,
        "friendly_pawn_promotion_distance": 1,
        "enemy_pawn_promotion_distance": 1,
        "can_castle": 1,
        "can_en_passant": 1,
        "num_legal_moves": 1
    }

    start = time.perf_counter()

    result = play_game(weights_bot1, weights_bot2, search_depth=1, replayable=True)
    print("Winner:", result[0])
    view_replay(result[1])
    print("Time taken:", time.perf_counter() - start)

