from dwave.system import DWaveSampler, EmbeddingComposite
sampler = EmbeddingComposite(DWaveSampler())

# Rook at bottom left
board = [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
valid_squares = [[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]]
#valid_squares_str = "0111100010001000"
#valid_squares = int(valid_squares_str, 2)

linear = {}
quadratic = {}

def add_weight_linear(constraint_id, weight):
    if constraint_id in linear: linear[constraint_id] += weight
    else: linear[constraint_id] = weight
def add_weight_quadratic(constraint_id, weight):
    if constraint_id in linear: quadratic[constraint_id] += weight
    else: quadratic[constraint_id] = weight

def apply_valid_squares():
    scale = 1
    #for i in range(16):

        #num_bits = valid_squares.bit_length()
        #sqr_is_valid = num >> (num_bits - 1)
        #sqr_is_valid = valid_squares << 1

    for x in range(4):
        for y in range(4):
            id = x * 4 + y
            if valid_squares[x][y] == 0: add_weight_linear((id, id), 1 * scale)
            else: add_weight_linear((id, id), -1 * scale)

def add_n_pieces_constraint(n):
    scale = 2
    for i in range(16):
        add_weight_linear((i, i), (-2*n + 1) * scale)
        for j in range(i+1, 16):
            add_weight_quadratic((i, j), 2 * scale)

def choose_move(attack_bitboard):
    print("under construction")

def parse_output(qubo_output):
    output = []
    for el in qubo_output['record']:
        output = output + el

    return output

apply_valid_squares()
add_n_pieces_constraint(1)

Q = {**linear, **quadratic}

sampleset = sampler.sample_qubo(Q, num_reads=20)
#print(linear)
#print(quadratic)
print(sampleset)
print(parse_output(sampleset))