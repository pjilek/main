#
# Web based GUI for BBC chess engine
#

# packages
import os
import sys
import random
import chess

from flask import Flask
from flask import render_template
from flask import request

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from qmover import get_move

# create web app instance
app = Flask(__name__)

# root(index) route
@app.route('/')
def root():
    return render_template('gui.html')

# make move API
@app.route('/make_move', methods=['POST'])
def make_move():
    # extract FEN string from HTTP POST request body
    fen = request.form.get('fen')

    # init python chess board instance
    board = chess.Board(fen)
    print("HUMAN PLAYED THIS")
    print(board)
    print("-----------------")
    
    if not board.is_checkmate():
        # find the rooks
        rook_mask = board.pieces_mask(chess.ROOK, chess.BLACK)
        rook_set = chess.SquareSet(rook_mask)
        # get attack map for each rook (bitboard of valid squares to move to)
        attack_sets = {}
        for rook in rook_set:
            attacks = board.attacks(rook)
            for sq, piece in board.piece_map().items():
                if sq in attacks:
                    if piece.color == chess.BLACK:
                        attacks.discard(sq)

            attack_sets.update({rook: attacks})

        # play a QUANTUM move !!
        print(board.piece_map())
        for rook, attack in attack_sets.items():
            print(f"ROOK AT POS {rook}")
            print(attack)
            print(hex(attack))
            move = get_move(int(attack))
            move_set = chess.SquareSet(move)
            print(f" ---- QUANTUM SAYS -----")
            print(hex(move))
            print(move_set)
            move_bit = move.bit_length() - 1
            print("move bit is", move_bit)
            computer_move = chess.Move(rook, chess.Square(move_bit))

        """
        # play a random move
        for i in range(0, 1000):
            legal_moves = []
            for j in board.legal_moves:
                legal_moves.append(j)
            computer_move = chess.Move.from_uci(str(random.choice(legal_moves)))
        """

        # update internal python chess board state
        print(f"COMPUTER WILL PLAY {computer_move}")
        board.push(computer_move)
    
    # extract FEN from current board state
    fen = board.fen()
    print(board)
    print("-----------------")
    
    return {'fen': fen}

# main driver
if __name__ == '__main__':
    # start HTTP server
    app.run(debug=True, threaded=True)
