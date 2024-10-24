from dwave.system import DWaveSampler, EmbeddingComposite
sampler = EmbeddingComposite(DWaveSampler())
linear = {}
quadratic = {}

def add_weight_linear(constraint_id, weight):
    if constraint_id in linear: linear[constraint_id] += weight
    else: linear[constraint_id] = weight
def add_weight_quadratic(constraint_id, weight):
    if constraint_id in quadratic: quadratic[constraint_id] += weight
    else: quadratic[constraint_id] = weight

# Reward squares that pieces can move to
def apply_valid_squares(attack_bitboards, board_size):
    linear.clear()
    quadratic.clear()

    print("apply_valid_squares")
    scale = 1

    # deconstruct the dictionaries
    for piece, bitboard in attack_bitboards.items():
        for i in range(board_size):
            id = f"{piece}{i}"
            sqr_is_valid = (bitboard & (1 << i))
            if sqr_is_valid: add_weight_linear((id, id), -1 * scale)

# Make sure only one move is selected
def add_n_pieces_constraint(n):
    print("add_n_pieces_constraint")
    scale = 10
    # loop through linear weights
    keys = list(linear.keys())

    for i in range(len(keys)):
        id1 = keys[i][0]
        add_weight_linear((id1, id1), (-2*n + 1) * scale)
        # print((id1, id1))
        for j in range(i + 1, len(keys)):
            id2 = keys[j][0]
            add_weight_quadratic((id1, id2), 2 * scale)
            # print((id1, id2))

def incentivise_taking(opponent_bitboard, board_size):
    piece_vals = {'r': 5, 'b': 3, 'q': 9, 'k': 100}
    
    scale = 10
    # go through linear constraints, if the location is a 1 in opponent_bitboard, add reward
    for key in linear.keys():
        id = key[0]  #r12
        location = int(id[1:])  #12
        sqr_has_piece = (opponent_bitboard & (1 << location))
        if (sqr_has_piece > 0): add_weight_linear(key, -1 * scale)
    
    print("LINEAR WITH OPPONENT PIECE WEIGHTS")
    print(linear)

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

# attackbitboards is a dictionary of form: key: 'r' value: 64bit integer
def get_move(attack_bitboards, opponent_bitboard, board_size = 64):
    apply_valid_squares(attack_bitboards, board_size)
    add_n_pieces_constraint(1)
    incentivise_taking(opponent_bitboard, board_size)
    Q = {**linear, **quadratic}
    sampleset = sampler.sample_qubo(Q, num_reads=500)
    #print(sampleset)
    return parse_output(sampleset)

# print(get_move(attack_bitboards, 16))