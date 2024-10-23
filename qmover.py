from dwave.system import DWaveSampler, EmbeddingComposite
sampler = EmbeddingComposite(DWaveSampler())
linear = {}
quadratic = {}

def add_weight_linear(constraint_id, weight):
    if constraint_id in linear: linear[constraint_id] += weight
    else: linear[constraint_id] = weight
def add_weight_quadratic(constraint_id, weight):
    if constraint_id in linear: quadratic[constraint_id] += weight
    else: quadratic[constraint_id] = weight

def apply_valid_squares(valid_squares):
    scale = 1
    for i in range(64):
        sqr_is_valid = (valid_squares >> (63-i)) & 1
        if sqr_is_valid == 1: add_weight_linear((i, i), -1 * scale)
        else: add_weight_linear((i, i), 1 * scale)

def add_n_pieces_constraint(n):
    scale = 2
    for i in range(64):
        add_weight_linear((i, i), (-2*n + 1) * scale)
        for j in range(i+1, 64):
            add_weight_quadratic((i, j), 2 * scale)

def parse_output(qubo_output):
    output = []
    result = 0
    for el in qubo_output.record:
        output = output + [el[0].tolist()]
    output = qubo_output.record[0][0].tolist()
    
    for i in range(len(output)):
        j = len(output) - 1 - i
        result += output[j] * 2**i
    return result

def get_move(attack_bitboard):
    apply_valid_squares(attack_bitboard)
    add_n_pieces_constraint(1)
    Q = {**linear, **quadratic}
    sampleset = sampler.sample_qubo(Q, num_reads=200)
    print("HERE IS THE SAMPLE SET")
    print(sampleset)
    print("HERE IS THE SAMPLE SET")
    return parse_output(sampleset)

#valid_squares_str = "0111100010001000"
#valid_squares = int(valid_squares_str, 2)
#move = get_move(valid_squares)
#print(move)