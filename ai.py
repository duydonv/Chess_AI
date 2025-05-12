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
    move_number = getattr(board, 'move_number', 0)
    if move_number <= 10:
        use_pos = False
        tables = None
    elif move_number >= 40:
        use_pos = True
        tables = PIECE_TABLES_ENDGAME
    else:
        use_pos = True
        tables = PIECE_TABLES
    center_squares = [(3,3), (3,4), (4,3), (4,4)]
    white_castled = False
    black_castled = False
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
                center_bonus = 0
                if (row, col) in center_squares:
                    center_bonus = 20
                # Khuyến khích phát triển quân nhẹ
                develop_bonus = 0
                if piece.name in ('knight', 'bishop'):
                    if (piece.color == 'white' and row > 0) or (piece.color == 'black' and row < 7):
                        develop_bonus = 30
                # Kiểm tra nhập thành
                castle_bonus = 0
                if piece.name == 'king':
                    if piece.color == 'white' and row == 7 and col != 4:
                        white_castled = True
                    if piece.color == 'black' and row == 0 and col != 4:
                        black_castled = True
                if piece.color == color:
                    total += value + 0.1 * pos_score + center_bonus + develop_bonus
                else:
                    total -= value + 0.1 * pos_score + center_bonus + develop_bonus
    # Cộng điểm nhập thành
    if color == 'white' and white_castled:
        total += 50
    if color == 'black' and black_castled:
        total += 50
    return total

def generate_legal_moves(board, color):
    legal_moves = []
    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]
            if square.has_piece() and square.piece.color == color:
                piece = square.piece
                board.calc_moves(piece, row, col, bool=True)
                for move in piece.moves:
                    # Thử đi nước cờ
                    initial = move.initial
                    final = move.final
                    captured = board.squares[final.row][final.col].piece
                    board.squares[initial.row][initial.col].piece = None
                    board.squares[final.row][final.col].piece = piece
                    # Kiểm tra vua có bị chiếu không
                    king_in_check = False
                    # Tìm vị trí vua
                    king_pos = None
                    for r in range(8):
                        for c in range(8):
                            p = board.squares[r][c].piece
                            if p and p.name == 'king' and p.color == color:
                                king_pos = (r, c)
                    if king_pos:
                        opponent = 'black' if color == 'white' else 'white'
                        for r in range(8):
                            for c in range(8):
                                op = board.squares[r][c].piece
                                if op and op.color == opponent:
                                    board.calc_moves(op, r, c, bool=True)
                                    for m in op.moves:
                                        if m.final.row == king_pos[0] and m.final.col == king_pos[1]:
                                            king_in_check = True
                    # Hoàn tác nước đi
                    board.squares[initial.row][initial.col].piece = piece
                    board.squares[final.row][final.col].piece = captured
                    if not king_in_check:
                        legal_moves.append((piece, move))
    return legal_moves

def minimax(board, depth, alpha, beta, maximizing_player, color):
    if depth == 0:
        return evaluate_board(board, color)
    current_color = color if maximizing_player else ('black' if color == 'white' else 'white')
    moves = generate_legal_moves(board, current_color)
    if not moves:
        # Không còn nước đi, kiểm tra chiếu hết/hòa
        # Tìm vị trí vua
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board.squares[r][c].piece
                if p and p.name == 'king' and p.color == current_color:
                    king_pos = (r, c)
        in_check = False
        if king_pos:
            opponent = 'black' if current_color == 'white' else 'white'
            for r in range(8):
                for c in range(8):
                    op = board.squares[r][c].piece
                    if op and op.color == opponent:
                        board.calc_moves(op, r, c, bool=True)
                        for m in op.moves:
                            if m.final.row == king_pos[0] and m.final.col == king_pos[1]:
                                in_check = True
        if in_check:
            return -math.inf if maximizing_player else math.inf
        else:
            return 0
    if maximizing_player:
        max_eval = -math.inf
        for piece, move in moves:
            initial = move.initial
            final = move.final
            captured = board.squares[final.row][final.col].piece
            board.squares[initial.row][initial.col].piece = None
            board.squares[final.row][final.col].piece = piece
            eval = minimax(board, depth-1, alpha, beta, False, color)
            board.squares[initial.row][initial.col].piece = piece
            board.squares[final.row][final.col].piece = captured
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for piece, move in moves:
            initial = move.initial
            final = move.final
            captured = board.squares[final.row][final.col].piece
            board.squares[initial.row][initial.col].piece = None
            board.squares[final.row][final.col].piece = piece
            eval = minimax(board, depth-1, alpha, beta, True, color)
            board.squares[initial.row][initial.col].piece = piece
            board.squares[final.row][final.col].piece = captured
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, color, depth=3):
    best_move = None
    best_eval = -math.inf
    moves = generate_legal_moves(board, color)
    for piece, move in moves:
        initial = move.initial
        final = move.final
        captured = board.squares[final.row][final.col].piece
        board.squares[initial.row][initial.col].piece = None
        board.squares[final.row][final.col].piece = piece
        eval = minimax(board, depth-1, -math.inf, math.inf, False, color)
        board.squares[initial.row][initial.col].piece = piece
        board.squares[final.row][final.col].piece = captured
        if eval > best_eval:
            best_eval = eval
            best_move = (piece, move)
    if best_move:
        return best_move[1]
    return None 