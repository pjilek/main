import chess

def gen_attack_bitboards(board : chess.Board, colour : chess.Color):
    attack_sets = {}
    for sq, piece in board.piece_map().items():
        if piece.color == colour:
            # get attack bitboard for this piece
            attacks = board.attacks(sq)
            for s, p in board.piece_map().items():
                # discard friendly-fire
                if s in attacks and p.color == colour:
                    attacks.discard(s)
            # create dictionary entry
            piece_id = f"{piece.symbol()}@{sq}"
            attack_sets.update({piece_id: int(attacks)})

    return attack_sets

def gen_move_bitboards(board : chess.Board, colour : chess.Color):
    attack_sets = {}
    for sq, piece in board.piece_map().items():
        if piece.color == colour:
            # get attack bitboard for this piece
            moves = board.attacks(sq)
            moves = board.find_move()
            print("PRE:", piece)
            print(moves)
            for s, p in board.piece_map().items():
                # discard friendly-fire
                if s in moves and p.color == colour:
                    moves.discard(s)
            print("POST:", piece)
            print(moves)
            piece_id = f"{piece.symbol()}@{sq}"
            attack_sets.update({piece_id: int(moves)})

    return attack_sets
