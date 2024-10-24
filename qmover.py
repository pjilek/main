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
    move_sets = {}
    for sq, piece in board.piece_map().items():
        if piece.color == colour:
            #print(f"----{piece}----")
            moves = board.attacks(sq)
            #print(moves)
            #print("----")
            if piece.piece_type == chess.PAWN:
                for s in moves:
                    # pawns cannot attack if no piece is there
                    if not board.piece_at(s):
                        moves.discard(s)
                #print(moves)
                #print("--remove attacks--")
                try:
                    # add forward movement if possible
                    file = chess.square_file(sq)
                    rank = chess.square_rank(sq) - 1
                    # this throws if no valid move
                    advance = board.find_move(sq, chess.square(file, rank))
                except Exception:
                    # this pawn is blocked
                    pass
                else:
                    try:
                        # if first move, then 2 ranks is possible
                        advance = board.find_move(sq, chess.square(file, rank-1))
                        moves.add(chess.square(file, rank-1))
                    except Exception:
                        pass
                    # add forward advance
                    moves.add(chess.square(file, rank))
                #print(moves)
                #print("----add 2 rank move----")
            for s, p in board.piece_map().items():
                # discard friendly-fire
                if s in moves and p.color == colour:
                    moves.discard(s)
            # create dictionary
            piece_id = f"{piece.symbol()}@{sq}"
            move_sets.update({piece_id: int(moves)})
            #print(moves)
            #print("--done (no friendly fire)--")

    return move_sets
