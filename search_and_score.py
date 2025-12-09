# This bit of code will simply attempt to build a search tree using python-chess from a starting position.

import chess


def build_search_tree(board:chess.Board, depth:int=1) -> dict:
    """
    Given a board state, build a tree of all valid moves down ot a certain depth, keeping the board states of the leaves.
    The resulting tree is represented as a nested dictionary, in which each entry is labeled with the move that led to that position.
    """
    if depth == 0:
        return {'board': board.fen()}

    tree = {}
    for move in board.legal_moves:
        board.push(move)
        tree[str(move)] = build_search_tree(board, depth - 1)
        board.pop()
    
    return tree


def score_move(board:chess.Board, is_player_white:bool, weights:dict) -> float:
    """
    Returns a score for the given board, evaluating it's "goodness" for the specified player.

    weights is the weighting applied to each rule.

    Rules:
    Material count , one rule for each piece, in order: pawn, knight, bishop, rook, queen, king, and then again for the opponent's pieces
    Do we have more pieces than the opponent? (simple yes/no)
    Number of friendly protected pieces (as in, another piece is covering it)
    Is the king in check? (2 rules, ours and theirs)
    Is the king in checkmate? (2 rules, ours and theirs)
    How close to the king are the enemy pieces? (horizontal and vertical)
    How close to the enemy king are our pieces? (horizontal and vertical)
    How many pieces are in the center? (friendly and enemy)
    How many of pieces are threatening unprotected pieces? (friendly and enemy)
    How close are pawns to promoting? (as in distance to last row, friendly and enemy)
    Can we castle? :D
    Can we En passant? UwU
    Number of legal moves available
    """

    score = 0

    friendly_color = chess.WHITE if is_player_white else chess.BLACK
    enemy_color = chess.BLACK if is_player_white else chess.WHITE

    # Friendly Material rules
    num_friendly_pawns = len(board.pieces(chess.PAWN, friendly_color))
    score += weights["friendly_pawn_count"] * num_friendly_pawns

    num_friendly_knights = len(board.pieces(chess.KNIGHT, friendly_color))
    score += weights["friendly_knight_count"] * num_friendly_knights

    num_friendly_bishops = len(board.pieces(chess.BISHOP, friendly_color))
    score += weights["friendly_bishop_count"] * num_friendly_bishops

    num_friendly_rooks = len(board.pieces(chess.ROOK, friendly_color))
    score += weights["friendly_rook_count"] * num_friendly_rooks

    num_friendly_queens = len(board.pieces(chess.QUEEN, friendly_color))
    score += weights["friendly_queen_count"] * num_friendly_queens

    num_friendly_kings = len(board.pieces(chess.KING, friendly_color))
    score += weights["friendly_king_count"] * num_friendly_kings

    # Enemy Material rules
    num_enemy_pawns = len(board.pieces(chess.PAWN, enemy_color))
    score -= weights["enemy_pawn_count"] * num_enemy_pawns

    num_enemy_knights = len(board.pieces(chess.KNIGHT, enemy_color))
    score -= weights["enemy_knight_count"] * num_enemy_knights

    num_enemy_bishops = len(board.pieces(chess.BISHOP, enemy_color))
    score -= weights["enemy_bishop_count"] * num_enemy_bishops

    num_enemy_rooks = len(board.pieces(chess.ROOK, enemy_color))
    score -= weights["enemy_rook_count"] * num_enemy_rooks

    num_enemy_queens = len(board.pieces(chess.QUEEN, enemy_color))
    score -= weights["enemy_queen_count"] * num_enemy_queens

    num_enemy_kings = len(board.pieces(chess.KING, enemy_color))
    score -= weights["enemy_king_count"] * num_enemy_kings

    # Total piece count
    total_friendly_pieces = (num_friendly_pawns + num_friendly_knights + num_friendly_bishops +
                             num_friendly_rooks + num_friendly_queens + num_friendly_kings)
    total_enemy_pieces = (num_enemy_pawns + num_enemy_knights + num_enemy_bishops +
                          num_enemy_rooks + num_enemy_queens + num_enemy_kings)
    
    score += weights["we_have_more"] * (1 if total_friendly_pieces > total_enemy_pieces else -1)

    # How many of our pieces are protected
    num_protected_friendly_pieces = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == friendly_color:
            attackers = board.attackers(not piece.color, square)
            if attackers:
                num_protected_friendly_pieces += 1
    
    score += weights["friendly_protected_pieces"] * num_protected_friendly_pieces

    # Are we in check?
    if board.is_check() and (board.turn == friendly_color):
        score -= weights["friendly_in_check"]
    else:
        score += weights["friendly_in_check"]

    # Is enemy in check?
    if board.is_check() and (board.turn == enemy_color):
        score += weights["enemy_in_check"]
    else:
        score -= weights["enemy_in_check"]

    # Are we in checkmate
    if board.is_checkmate() and (board.turn == friendly_color):
        score -= weights["friendly_in_checkmate"]
    else:
        score += weights["friendly_in_checkmate"]
    
    # Is enemy in checkmate
    if board.is_checkmate() and (board.turn == enemy_color):
        score += weights["enemy_in_checkmate"]
    else:
        score -= weights["enemy_in_checkmate"]
    
    # How close to our king are enemy pieces
    friendly_king_square = board.king(friendly_color)
    enemy_piece_proximity = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == enemy_color:
            enemy_piece_proximity += chess.square_distance(square, friendly_king_square)
    score += weights["enemy_proximity_to_friendly_king"] * enemy_piece_proximity

    # How close are we to the enemy king
    enemy_king_square = board.king(enemy_color)
    friendly_piece_proximity = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == friendly_color:
            friendly_piece_proximity += chess.square_distance(square, enemy_king_square)
    score -= weights["friendly_proximity_to_enemy_king"] * friendly_piece_proximity

    # Are we in the power position of chess, commonly refered to as "the center"?
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    num_friendly_center_pieces = 0
    for square in center_squares:
        piece = board.piece_at(square)
        if piece and piece.color == friendly_color:
            num_friendly_center_pieces += 1
    score += weights["friendly_center_control"] * num_friendly_center_pieces

    # Does the enemy have the center?
    num_enemy_center_pieces = 0
    for square in center_squares:
        piece = board.piece_at(square)
        if piece and piece.color == enemy_color:
            num_enemy_center_pieces += 1
    score -= weights["enemy_center_control"] * num_enemy_center_pieces

    # Are we threatening unprotected enemy pieces?
    unprotected_enemies = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == enemy_color:
            attackers = board.attackers(friendly_color, square)
            defenders = board.attackers(enemy_color, square)
            if attackers and not defenders:
                unprotected_enemies += 1
    score += weights["friendly_threatening_unprotected"] * unprotected_enemies

    # Is the enemy threatening unprotected friendly pieces?
    unprotected_friendlies = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == friendly_color:
            attackers = board.attackers(enemy_color, square)
            defenders = board.attackers(friendly_color, square)
            if attackers and not defenders:
                unprotected_friendlies += 1
    score -= weights["enemy_threatening_unprotected"] * unprotected_friendlies

    # How close are friendly pawns to promoting?
    friendly_pawn_promotion_distance = 0
    for square in board.pieces(chess.PAWN, friendly_color):
        rank = chess.square_rank(square)
        if is_player_white:
            friendly_pawn_promotion_distance += (9 - rank)
        else:
            friendly_pawn_promotion_distance += rank
    score -= weights["friendly_pawn_promotion_distance"] * friendly_pawn_promotion_distance

    # How close are enemy pawns to promoting?
    enemy_pawn_promotion_distance = 0
    for square in board.pieces(chess.PAWN, enemy_color):
        rank = chess.square_rank(square)
        if is_player_white:
            enemy_pawn_promotion_distance += rank
        else:
            enemy_pawn_promotion_distance += (9 - rank)
    score += weights["enemy_pawn_promotion_distance"] * enemy_pawn_promotion_distance

    # Can we castle?
    if board.has_kingside_castling_rights(friendly_color) or board.has_queenside_castling_rights(friendly_color):
        score -= weights["can_castle"]
    else:
        score += weights["can_castle"]
    
    # Can we En passant?
    if board.has_legal_en_passant():
        score += weights["can_en_passant"]
    else:
        score -= weights["can_en_passant"]
    
    # Number of legal moves available
    num_legal_moves = board.legal_moves.count()
    score += weights["num_legal_moves"] * num_legal_moves

    return score


def score_tree(tree:dict, is_player_white:bool, weights:dict) -> dict:
    """
    Given a search tree as produced by build_search_tree, score each leaf node using score_move, and propagate the scores up the tree.
    The resulting tree will have the same structure, but each node will have an additional entry "score" with the computed score.
    """
    if 'board' in tree:
        board = chess.Board(tree['board'])
        tree['score'] = score_move(board, is_player_white, weights)
        return tree

    for move, subtree in tree.items():
        scored_subtree = score_tree(subtree, is_player_white, weights)
        tree[move] = scored_subtree

    # After scoring all children, we can compute the score for this node
    if tree:
        tree['score'] = max(subtree['score'] for subtree in tree.values() if isinstance(subtree, dict))
    else:
        tree['score'] = 0  # No moves available

    return tree


if __name__ == "__main__":
    import time
    
    weights={
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
        "friendly_protected_pieces": 1,
        "friendly_in_check": 1,
        "enemy_in_check": 1,
        "friendly_in_checkmate": 1,
        "enemy_in_checkmate": 1,
        "enemy_proximity_to_friendly_king": 1,
        "friendly_proximity_to_enemy_king": 1,
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

    borbd = chess.Board()
    
    print(borbd.turn)
    print(borbd.legal_moves)
    print(borbd)

    test_move = chess.Move.from_uci("e2e4")
    borbd.push(test_move)

    print(borbd.turn)
    print(borbd.legal_moves)
    print(borbd)

    borbd.pop()

    start = time.perf_counter()

    test_tree = build_search_tree(borbd, depth=3)

    test_tree = score_tree(test_tree, is_player_white=True, weights=weights)

    #print(test_tree)
    
    print(f"Tame taken: {time.perf_counter() - start:.4} sec")

