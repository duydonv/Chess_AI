import math

# Bảng điểm vị trí đơn giản cho từng quân (giá trị cho white, black sẽ đảo ngược)
PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0, 0, 0, 0, 0, 0, 0, 0]
]
KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]
BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]
ROOK_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0]
]
QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]
KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

PIECE_TABLES = {
    'pawn': PAWN_TABLE,
    'knight': KNIGHT_TABLE,
    'bishop': BISHOP_TABLE,
    'rook': ROOK_TABLE,
    'queen': QUEEN_TABLE,
    'king': KING_TABLE
}

# Bảng điểm vị trí tàn cuộc đơn giản (có thể mở rộng sau)
PAWN_TABLE_ENDGAME = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [10, 10, 10, 10, 10, 10, 10, 10],
    [20, 20, 20, 20, 20, 20, 20, 20],
    [30, 30, 30, 30, 30, 30, 30, 30],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [60, 60, 60, 60, 60, 60, 60, 60],
    [0, 0, 0, 0, 0, 0, 0, 0]
]
KNIGHT_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
BISHOP_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
ROOK_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
QUEEN_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
KING_TABLE_ENDGAME = [
    [-10, -10, -10, -10, -10, -10, -10, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 10, 20, 20, 20, 20, 10, -10],
    [-10, 10, 20, 30, 30, 20, 10, -10],
    [-10, 10, 20, 30, 30, 20, 10, -10],
    [-10, 10, 20, 20, 20, 20, 10, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, -10, -10, -10, -10, -10, -10, -10]
]
PIECE_TABLES_ENDGAME = {
    'pawn': PAWN_TABLE_ENDGAME,
    'knight': KNIGHT_TABLE_ENDGAME,
    'bishop': BISHOP_TABLE_ENDGAME,
    'rook': ROOK_TABLE_ENDGAME,
    'queen': QUEEN_TABLE_ENDGAME,
    'king': KING_TABLE_ENDGAME
}

def evaluate_board(board, color):
    piece_values = {
        'pawn': 100,
        'knight': 320,
        'bishop': 330,
        'rook': 500,
        'queen': 900,
        'king': 0
    }
    total = 0
    # Xác định số nước đi (move_number)
    move_number = getattr(board, 'move_number', 0)
    # Xác định bảng điểm vị trí theo giai đoạn
    if move_number <= 10:
        use_pos = False
        tables = None
    elif move_number >= 40:
        use_pos = True
        tables = PIECE_TABLES_ENDGAME
    else:
        use_pos = True
        tables = PIECE_TABLES
    # Các ô trung tâm
    center_squares = [(3,3), (3,4), (4,3), (4,4)]
    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]
            if square.has_piece():
                piece = square.piece
                value = piece_values.get(piece.name, 0)
                pos_score = 0
                if use_pos and tables:
                    table = tables.get(piece.name)
                    if table:
                        pos_score = table[row][col] if piece.color == 'white' else table[7-row][col]
                # Điểm kiểm soát trung tâm
                center_bonus = 0
                if (row, col) in center_squares:
                    center_bonus = 20
                if piece.color == color:
                    total += value + 0.1 * pos_score + center_bonus
                else:
                    total -= value + 0.1 * pos_score + center_bonus
    return total

def minimax(board, depth, alpha, beta, maximizing_player, color, cache):
    board_state = board.get_board_state()
    if (board_state, depth, maximizing_player) in cache:
        return cache[(board_state, depth, maximizing_player)]
    if depth == 0:
        eval_score = evaluate_board(board, color)
        cache[(board_state, depth, maximizing_player)] = eval_score
        return eval_score
    moves = []
    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]
            if square.has_piece() and square.piece.color == (color if maximizing_player else ('black' if color == 'white' else 'white')):
                piece = square.piece
                board.calc_moves(piece, row, col)
                for move in piece.moves:
                    moves.append((piece, move))
    if not moves:
        # Không còn nước đi, kiểm tra chiếu hết/hòa
        from game import Game
        game = Game()
        game.board = board
        if game.is_checkmate(color if maximizing_player else ('black' if color == 'white' else 'white')):
            return -math.inf if maximizing_player else math.inf
        else:
            return 0
    if maximizing_player:
        max_eval = -math.inf
        for piece, move in moves:
            # Thực hiện nước đi tạm thời
            initial = move.initial
            final = move.final
            captured = board.squares[final.row][final.col].piece
            board.squares[initial.row][initial.col].piece = None
            board.squares[final.row][final.col].piece = piece
            eval = minimax(board, depth-1, alpha, beta, False, color, cache)
            # Hoàn tác nước đi
            board.squares[initial.row][initial.col].piece = piece
            board.squares[final.row][final.col].piece = captured
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        cache[(board_state, depth, maximizing_player)] = max_eval
        return max_eval
    else:
        min_eval = math.inf
        for piece, move in moves:
            # Thực hiện nước đi tạm thời
            initial = move.initial
            final = move.final
            captured = board.squares[final.row][final.col].piece
            board.squares[initial.row][initial.col].piece = None
            board.squares[final.row][final.col].piece = piece
            eval = minimax(board, depth-1, alpha, beta, True, color, cache)
            # Hoàn tác nước đi
            board.squares[initial.row][initial.col].piece = piece
            board.squares[final.row][final.col].piece = captured
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        cache[(board_state, depth, maximizing_player)] = min_eval
        return min_eval

def find_best_move(board, color, depth=3):
    best_move = None
    best_eval = -math.inf
    cache = {}
    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]
            if square.has_piece() and square.piece.color == color:
                piece = square.piece
                board.calc_moves(piece, row, col)
                for move in piece.moves:
                    # Thực hiện nước đi tạm thời
                    initial = move.initial
                    final = move.final
                    captured = board.squares[final.row][final.col].piece
                    board.squares[initial.row][initial.col].piece = None
                    board.squares[final.row][final.col].piece = piece
                    eval = minimax(board, depth-1, -math.inf, math.inf, False, color, cache)
                    # Hoàn tác nước đi
                    board.squares[initial.row][initial.col].piece = piece
                    board.squares[final.row][final.col].piece = captured
                    if eval > best_eval:
                        best_eval = eval
                        best_move = (piece, move)
    if best_move:
        return best_move[1]
    return None 