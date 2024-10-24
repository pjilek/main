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
    scale = 1
    
    # deconstruct the dictionaries
    for piece in attack_bitboards:
        attack_bitboard = attack_bitboards[piece]
        for i in range(board_size):
            id = f"{piece}{i}"
            sqr_is_valid = (attack_bitboard >> (board_size-1-i)) & 1
            if sqr_is_valid == 1: add_weight_linear((id, id), -1 * scale)
    
# Make sure only one move is selected
def add_n_pieces_constraint(n):
    print(linear)
    scale = 2
    # loop through linear weights
    keys = list(linear.keys())

    for i in range(len(keys)):
        id1 = keys[i][0]
        add_weight_linear((id1, id1), (-2*n + 1) * scale)
        print((id1, id1))
        for j in range(i + 1, len(keys)):
            id2 = keys[j][0]
            add_weight_quadratic((id1, id2), 2 * scale)
            print((id1, id2))

def parse_output(qubo_output):
    output = []
    for el in qubo_output.record:
        output = output + [el[0].tolist()]
    output = qubo_output.record[0][0].tolist()
    print(qubo_output.variables)

    for i, label in enumerate(qubo_output.variables):
        bit = output[i]
        if bit: return label

valid_squares_str_rook = "0111100010001000"
valid_squares_str_king = "0000010010100100"
valid_squares_rook = int(valid_squares_str_rook, 2)
valid_squares_king = int(valid_squares_str_king, 2)
attack_bitboards = {'r': valid_squares_rook, 'k': valid_squares_king}

# attackbitboards is a dictionary of form: key: 'r' value: 64bit integer
def get_move(attack_bitboards, board_size = 64):
    apply_valid_squares(attack_bitboards, board_size)
    add_n_pieces_constraint(1)
    Q = {**linear, **quadratic}
    sampleset = sampler.sample_qubo(Q, num_reads=50)
    print(sampleset)
    return parse_output(sampleset)

print(get_move(attack_bitboards, 16))