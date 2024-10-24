from dimod import (
    Binary,
    BinaryQuadraticModel,
    ConstrainedQuadraticModel,
    quicksum,
)
from dwave.system import LeapHybridCQMSampler
from qmover import gen_attackers_list

pst = {
    'p': (   0,   0,   0,   0,   0,   0,   0,   0,
              -78,  -83,  -86,  -73, -102,  -82,  -85,  -90,
              -7,  -29,  -21,  -44,  -40,  -31,  -44,   -7,
            17,  -16,  2,  -15,  -14,   0,  -15, +13,
            26,   -3,  -10,   -9,   -6,   -1,   0, 23,
            22,   -9,   -5, 11, 10,  2,   -3, 19,
            31,   -8,  7, 37, 36, 14,   -3, 31,
              0,   0,   0,   0,   0,   0,   0,   0),
    'n': ( 66, 53, 75, 75, 10, 55, 58, 70,
              3,  6, -100, 36,   -4,  -62,  4, 14,
              -10,  -67,   -1,  -74,  -73,  -27,  -62,  2,
              -24,  -24,  -45,  -37,  -33,  -41,  -25,  -17,
              1,   -5,  -31,  -21,  -22,  -35,   -2,   0,
            18,  -10,  -13,  -22,  -18,  -15,  -11, 14,
            23, 15,   -2,   0,   -2,   0, 23, 20,
            74, 23, 26, 24, 19, 35, 22, 69),
    'b': ( 59, 78, 82, 76, 23, 107, 37, 50,
            11, -20, -35, 42, 39, -31, -2, 22,
              9,  -39, 32,  -41,  -52, 10,  -28, 14,
              -25,  -17,  -20,  -34,  -26,  -25,  -15,  -10,
              -13, -10, -17, -23, -17, -16, -0, -7,
              -14, -25, -24, -15, -8, -25, -20, -15,
              -19, -20, -11, -6, -7, -6, -20, -16,
              7, -2, 15, 12, 14, 15, 10, 10),
    'r': (  -35,  -29,  -33,   -4,  -37,  -33,  -56,  -50,
              -55,  -29,  -56,  -67,  -55,  -62,  -34,  -60,
              -19,  -35,  -28,  -33,  -45,  -27,  -25,  -15,
               0,   -5,  -16,  -13,  -18,  4,  9,  6,
            28, 35, 16, 21, 13, 29, 46, 30,
            42, 28, 42, 25, 25, 35, 26, 46,
            53, 38, 31, 26, 29, 43, 44, 53,
            -30, -24, -18,   5,  -2, -18, -31, -32),
    'q': (   -6,   -1,  8, 104,  -69,  -24,  -88,  -26,
              -14,  -32,  -60, 10,  -20,  -76,  -57,  -24,
              2,  -43,  -32,  -60,  -72,  -63,  -43,   -2,
               -1, 16,  -22,  -17,  -25,  -20, 13,  6,
            14, 15,  2,  5,  1, 10, 20, 22,
            30,  6, 13, 11, 16, 11, 16, 27,
            36, 18,   -0, 19, 15, 15, 21, 38,
            39, 30, 31, 13, 31, 36, 34, 42),
    'k': (   -4,  -54,  -47, 99, 99,  -60,  -83, 62,
            32,  -10,  -55,  -56,  -56,  -55,  -10,  -3,
            62,  -12, 57,  -44, 67,  -28,  -37, 31,
            55,  -50,  -11,  4, 19,  -13,   -0, 49,
            55, 43, 52, 28, 51, 47,  8, 50,
            47, 42, 43, 79, 64, 32, 29, 32,
              4,   -3, 14, 50, 57, 18,  -13,   -4,
              -17,  -30,  3, 14,   -6,  1,  -40,  -18)
}

# opponent_bitboards is a dictionary 'r' - bitboard
def build_cqm(attack_bitboards, opponent_bitboard, opponent_bitboards, board):  
    print(opponent_bitboards)  
    cqm = ConstrainedQuadraticModel()
    obj = BinaryQuadraticModel(vartype="BINARY")

    x = {}

    attack_defend_list = [0]*64
    # piece_attack_defend_multipliers = {'k': -75, 'q': -150, 'r': -225, 'b': -300, 'n': -300, 'p': -250,
    #                                    'K': 75, 'Q': 150, 'R': 225, 'B': 300, 'N': 300, 'P': 250}
    piece_attack_defend_multipliers = {'k': -50, 'q': -50, 'r': -50, 'b': -50, 'n': -50, 'p': -50,
                                       'K': 1000, 'Q': 1000, 'R': 1000, 'B': 1000, 'N': 1000, 'P': 1000}


    for sqr in range(64):
        # Decentivise moving to attacked spots
        for opp_attack_piece, opp_attack_bitboard in opponent_bitboards.items():
            square_is_attacked = (opp_attack_bitboard >> sqr) & 1 > 0
            if square_is_attacked:
                attack_defend_list[sqr] += piece_attack_defend_multipliers[opp_attack_piece.split("@")[0]]

        # Incentivise moving to defended spots
        for defend_piece, defend_bitboard in attack_bitboards.items():
            square_is_defended = (defend_bitboard >> sqr) & 1 > 0
            if square_is_defended:
                attack_defend_list[sqr] += piece_attack_defend_multipliers[defend_piece.split("@")[0]]

    piece_vals = {'K': 2000, 'Q': 900, 'R': 500, 'N': 300, 'B': 300, 'P': 100}
    capturer_multiplier = {'k': 0.3, 'q': 0.5, 'r': 0.7, 'b': 0.8, 'n': 0.8, 'p': 1}
    print(attack_defend_list)
    for piece, bitboard in attack_bitboards.items():
        for square in range(64):
            sqr_weight = 0

            # Set weights to positions
            square_is_reachable = (bitboard >> square) & 1
            piece_type, piece_loc = piece.split("@")
            if square_is_reachable: 
                sqr_weight = pst[piece_type][square] - pst[piece_type][int(piece_loc)]
                sqr_weight += attack_defend_list[square] #* capturer_multiplier[piece_type]
                sqr_weight -= piece_attack_defend_multipliers[piece_type]
                sqr_weight -= is_attacked_weight(int(piece_loc), piece_type, board)
            else: continue

            # Take opponents pieces
            opponent_in_square = (opponent_bitboard >> square) & 1
            if opponent_in_square:
                for opponent_piece in opponent_bitboards.keys():
                    oppPiece, loc = opponent_piece.split("@")
                    loc = int(loc)
                    if loc == square:
                        sqr_weight -= piece_vals[oppPiece]

            x[(piece, square)] = Binary(piece + "->" + str(square))
            obj += sqr_weight * x[(piece, square)]

    cqm.set_objective(obj)
    cqm.add_constraint(sum(x.values()) == 1)

    return cqm
def parse_output(qubo_output):
    output = []
    for el in qubo_output.record:
        output = output + [el[0].tolist()]
    output = qubo_output.record[0][0].tolist()
    print(qubo_output.variables)
    print(output)
    for i, label in enumerate(qubo_output.variables):
        bit = output[i]
        if bit: return label

def get_move(attack_bitboards, opponent_bitboard, opponent_bitboards, board):
    cqm = build_cqm(attack_bitboards, opponent_bitboard, opponent_bitboards, board)
    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm)
    feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)
    print(feasible_sampleset)
    return parse_output(feasible_sampleset)

def is_attacked_weight(square, piece_type, board):
    piece_vals = {'K': 2000, 'Q': 900, 'R': 500, 'N': 300, 'B': 300, 'P': 100, 'k': 20000, 'q': 20000, 'r': 20000, 'n': 20000, 'b': 20000, 'p': 20000 }
    victim_vals = {'k': 2000, 'q': 900, 'r': 500, 'n': 300, 'b': 300, 'p': 100}
    list_of_attackers = gen_attackers_list(board, square)
    
    weakest_attacker_val = 3000
    defended = False
    for attacker in list_of_attackers:
        attacker_type = attacker.split('@')[0]
        if piece_vals[attacker_type] < weakest_attacker_val:
            weakest_attacker_val = piece_vals[attacker_type]
        if piece_vals[attacker_type] == 20000:
            defended  = True

    if (weakest_attacker_val == 3000): return 0
    if not defended: return victim_vals[piece_type]

    if weakest_attacker_val < victim_vals[piece_type]: # if we are more valuable than attacking piece
        if defended: return (victim_vals[piece_type] -  weakest_attacker_val)
    else: return 0
        