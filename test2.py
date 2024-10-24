from dwave.system import DWaveSampler, EmbeddingComposite
sampler = EmbeddingComposite(DWaveSampler())
linear = {}
quadratic = {}

valid_squares_str_rook = "0111100010001000"
valid_squares_str_king = "0000010010100100"
valid_squares_rook = int(valid_squares_str_rook, 2)
valid_squares_king = int(valid_squares_str_king, 2)

def add_weight_linear(constraint_id, weight):
    if constraint_id in linear: linear[constraint_id] += weight
    else: linear[constraint_id] = weight
def add_weight_quadratic(constraint_id, weight):
    if constraint_id in quadratic: quadratic[constraint_id] += weight
    else: quadratic[constraint_id] = weight

# Reward squares that pieces can move to
def apply_valid_squares():
    scale = 1
    
    #ROOK
    for i in range(16):
        id = f'r{i}'
        sqr_is_valid = (valid_squares_rook >> (15-i)) & 1
        if sqr_is_valid == 1: add_weight_linear((id, id), -1 * scale)
        else: add_weight_linear((id, id), 1 * scale)

    #KING
    for i in range(16):
        id = f'k{i}'
        sqr_is_valid = (valid_squares_king >> (15-i)) & 1
        if sqr_is_valid == 1: add_weight_linear((id, id), -1 * scale)
        else: add_weight_linear((id, id), 1 * scale)
    

# Make sure only one move is selected
def add_n_pieces_constraint(n):
    scale = 6

    board_size = 16
    piece_prefixes = ['r', 'k']

    for i in range(board_size * len(piece_prefixes)):
        id = f'{piece_prefixes[i // board_size]}{i % 16}'
        add_weight_linear((id, id), (-2*n + 1) * scale)
        #print(f'linear: {(id, id)}')
        
        for j in range(i+1, board_size * len(piece_prefixes)):
            id2 = f'{piece_prefixes[j // board_size]}{j % 16}'
            add_weight_quadratic((id, id2), 2 * scale)
            #print(f'quadratic: {(id, id2)}')

def parse_output(qubo_output):
    output = []
    for el in qubo_output.record:
        output = output + [el[0].tolist()]
    output = qubo_output.record[0][0].tolist()
    print(output)

    #convert to int
    result = 0
    for i in range(len(output)):
        j = len(output) - 1 - i
        result += output[j] * 2**i
    print(result)
    print(bin(result))
    return result

def get_move():
    apply_valid_squares()
    add_n_pieces_constraint(1)
    Q = {**linear, **quadratic}
    sampleset = sampler.sample_qubo(Q, num_reads=500)
    print(sampleset)
    return parse_output(sampleset)

get_move()