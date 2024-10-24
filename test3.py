from dimod import (
    Binary,
    BinaryQuadraticModel,
    ConstrainedQuadraticModel,
    quicksum,
)
from dwave.system import LeapHybridCQMSampler

def valid_squares(attack_bitboards):
    moves_list = []
    for piece, bitboard in attack_bitboards.items():
        for square in range(64):
            if (bitboard >> (square)) & 1 == 1:
                moves_list.append((piece, square))
    return moves_list

def build_cqm(attack_bitboards, opponent_bitboard):
    cqm = ConstrainedQuadraticModel()
    obj = BinaryQuadraticModel(vartype="BINARY")
    x = {}

    # add valid moves to obj
    for piece, bitboard in attack_bitboards.items():
        for square in range(64):
            sqr_weight = 0

            square_is_reachable = (bitboard >> (square)) & 1 == 1
            if square_is_reachable: sqr_weight += -1
            opponent_in_square = (opponent_bitboard >> (square)) & 1 == 1
            if opponent_in_square: obj += -1

            if sqr_weight != 0:  
                obj += sqr_weight * Binary(piece + str(square))
                x[(piece, square)] = Binary(piece + str(square))

    # Objective: for infeasible solutions, focus on right number of shifts for employees
    cqm.set_objective(obj)

    print(valid_squares(attack_bitboards))

    # ensure only one piece is moved
    cqm.add_constraint(sum(x[piece, square] for piece, square in valid_squares(attack_bitboards)) == 1)
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

def get_move(attack_bitboards, opponent_bitboard, board_size = 64):
    cqm = build_cqm(attack_bitboards)
    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm)
    print(sampleset)
    feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)
    print(feasible_sampleset)
    return parse_output(feasible_sampleset)