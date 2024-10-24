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
from test3 import get_move
from qmover import gen_attack_bitboards

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
        attack_sets = gen_attack_bitboards(board, chess.BLACK)
        print("attack sets from app")
        print(attack_sets)
        # generate OR'd attack map of human pieces
        white_mask = 0
        for piece_type in chess.PIECE_TYPES:
            white_mask = white_mask | board.pieces_mask(piece_type, chess.WHITE)
        white_set = chess.SquareSet(white_mask)
        avoid_mask = 0
        for piece in white_set:
            attacks = board.attacks(piece)
            avoid_mask = avoid_mask | int(attacks)
        avoid_set = chess.SquareSet(avoid_mask)
        # print("SQARES TO AVOID")
        # print(avoid_set)

        # play a QUANTUM move !!
        print("HUMAN PIECES ARE HERE")
        #print(white_set)
        white_bitboards = gen_attack_bitboards(board, chess.WHITE)
        piece_and_move = get_move(attack_sets, white_mask, white_bitboards)
        piece, move = piece_and_move.split('->')
        move = int(move)
        # move_set = chess.SquareSet(move)
        print(f" ---- QUANTUM SAYS -----")
        print(piece, "to", move)
        symbol, loc = piece.split('@')
        #piece = board.pieces_mask(chess.Piece.from_symbol(piece).piece_type, chess.BLACK)
        #piece = piece.bit_length() - 1
        computer_move = chess.Move(chess.Square(loc), chess.Square(move))

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
