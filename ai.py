import math
from square import Square
from move import Move


# Bảng điểm vị trí đơn giản cho từng quân (giá trị cho white, black sẽ đảo ngược)
PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [100, 100, 100, 100, 100, 100, 100, 100]  # Điều chỉnh điểm đế khuyến khích AI phong quân
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
    [80, 80, 80, 80, 80, 80, 80, 80],
    [60, 60, 60, 60, 60, 60, 60, 60],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [20, 20, 20, 20, 20, 20, 20, 20],
    [10, 10, 10, 10, 10, 10, 10, 10],
    [5, 5, 5, 5, 5, 5, 5, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

#Bảng điểm tàn cuộc cho các quân khác, sẽ bổ sung sau nếu thấy cần thiết
KNIGHT_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
BISHOP_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
ROOK_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
QUEEN_TABLE_ENDGAME = [[0]*8 for _ in range(8)]
KING_TABLE_ENDGAME = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-20, -10, 20, 30, 30, 20, -10, -20],
    [-10, 0, 30, 40, 40, 30, 0, -10],
    [-10, 0, 30, 40, 40, 30, 0, -10],
    [-20, -10, 20, 30, 30, 20, -10, -20],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-50, -40, -30, -20, -20, -30, -40, -50]
]
PIECE_TABLES_ENDGAME = {
    'pawn': PAWN_TABLE_ENDGAME,
    'knight': KNIGHT_TABLE_ENDGAME,
    'bishop': BISHOP_TABLE_ENDGAME,
    'rook': ROOK_TABLE_ENDGAME,
    'queen': QUEEN_TABLE_ENDGAME,
    'king': KING_TABLE_ENDGAME
}

def get_opening_moves(move_number):
    """
    Trả về nước đi khai cuộc dựa trên số nước đã đi
    move_number là số nước đi của cả bàn cờ
    """
    # Sicilian Defense - một trong những khai cuộc mạnh nhất cho quân đen
    # Chia 2 vì move_number là số nước đi của cả bàn cờ
    ai_move_number = move_number // 2
    
    opening_moves = {
        1: {'initial': (1, 4), 'final': (3, 4)},  # e5
        2: {'initial': (0, 1), 'final': (2, 2)},  # Nc6
        3: {'initial': (1, 1), 'final': (2, 1)},  # b6
        4: {'initial': (0, 6), 'final': (2, 5)},  # Bb7
        5: {'initial': (0, 5), 'final': (1, 4)},  # phát triển tịnh
        6: {'initial': (0, 4), 'final': (0, 6)},  # O-O (nhập thành)
    }
    
    return opening_moves.get(ai_move_number)

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
    
    # Điều chỉnh logic chọn bảng điểm: khai cuộc, trung cuộc, tàn cuộc
    if move_number <= 10:
        use_pos = True
        tables = PIECE_TABLES  # Vẫn sử dụng bảng điểm thường
        # Tăng hệ số cho các yếu tố khai cuộc
        opening_factor = 1.5
    elif move_number >= 40:
        use_pos = True
        tables = PIECE_TABLES_ENDGAME
        opening_factor = 1.0
    else:
        use_pos = True
        tables = PIECE_TABLES
        opening_factor = 1.0

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
                
                # Tăng điểm cho các yếu tố khai cuộc
                center_bonus = 0
                if (row, col) in center_squares:
                    center_bonus = 20 * opening_factor

                develop_bonus = 0
                if piece.name in ('knight', 'bishop'):
                    if (piece.color == 'white' and row > 0) or (piece.color == 'black' and row < 7):
                        develop_bonus = 30 * opening_factor

                # Thêm bonus cho việc bảo vệ vua trong khai cuộc
                king_safety_bonus = 0
                if piece.name == 'king':
                    if piece.color == 'white' and row == 7 and col != 4:
                        white_castled = True
                    if piece.color == 'black' and row == 0 and col != 4:
                        black_castled = True
                    # Thêm điểm cho vua ở vị trí an toàn
                    if move_number <= 10:
                        if piece.color == 'white' and row == 7:
                            king_safety_bonus = 20
                        if piece.color == 'black' and row == 0:
                            king_safety_bonus = 20

                if piece.color == color:
                    total += value + 0.3 * pos_score + center_bonus + develop_bonus + king_safety_bonus
                else:
                    total -= value + 0.3 * pos_score + center_bonus + develop_bonus + king_safety_bonus

    # Tăng điểm nhập thành trong khai cuộc
    castle_bonus = 50 * opening_factor
    if color == 'white' and white_castled:
        total += castle_bonus
    if color == 'black' and black_castled:
        total += castle_bonus

    return total

def generate_legal_moves(board, color):
    legal_moves = []
    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]
            if square.has_piece() and square.piece.color == color:
                piece = square.piece
                board.calc_moves(piece, row, col, checking_checks=True)
                for move in piece.moves:
                    # Thử đi nước cờ
                    board.make_move(piece, move)
                    # Kiểm tra vua có bị chiếu không
                    king_in_check = board._is_king_in_check(color)
                    board.undo_move()
                    if not king_in_check:
                        legal_moves.append((piece, move))
    # Sắp xếp nước đi: nước ăn quân và phong hậu lên trước
    def move_score(item):
        piece, move = item
        captured = board.squares[move.final.row][move.final.col].piece
        # Ưu tiên nước ăn quân
        score = 0
        if captured is not None:
            score += 10 + getattr(captured, 'value', 1)
        # Ưu tiên phong hậu
        if piece.name == 'pawn' and (move.final.row == 0 or move.final.row == 7):
            score += 20
        return -score  # Sắp xếp giảm dần
    legal_moves.sort(key=move_score)
    return legal_moves

def minimax(board, depth, alpha, beta, maximizing_player, color):
    if depth == 0:
        return evaluate_board(board, color)
    current_color = color if maximizing_player else ('black' if color == 'white' else 'white')
    moves = generate_legal_moves(board, current_color)
    if not moves:
        # Không còn nước đi, kiểm tra chiếu hết/hòa
        if board._is_king_in_check(current_color):
            return -math.inf if maximizing_player else math.inf
        else:
            return 0
    if maximizing_player:
        max_eval = -math.inf
        for piece, move in moves:
            board.make_move(piece, move)
            eval = minimax(board, depth-1, alpha, beta, False, color)
            board.undo_move()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for piece, move in moves:
            board.make_move(piece, move)
            eval = minimax(board, depth-1, alpha, beta, True, color)
            board.undo_move()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, color, depth):
    # Thêm logic khai cuộc
    if color == 'black' and board.move_number < 12:  # 6 nước của AI = 12 nước của cả bàn cờ
        opening_move = get_opening_moves(board.move_number + 1)
        if opening_move:
            # Tìm quân cờ ở vị trí initial
            piece = board.squares[opening_move['initial'][0]][opening_move['initial'][1]].piece
            if piece and piece.color == color:
                # Tạo nước đi
                initial = Square(opening_move['initial'][0], opening_move['initial'][1])
                final = Square(opening_move['final'][0], opening_move['final'][1])
                move = Move(initial, final)
                # Kiểm tra nước đi hợp lệ
                if board.valid_move(piece, move):
                    print(f'AI di khai cuoc: {piece.name} tu {opening_move["initial"]} den {opening_move["final"]}')
                    return move
                else:
                     print('Nuoc khai cuoc khong hop le, chuyen sang minimax')
    # Nếu không có nước khai cuộc hoặc đã hết khai cuộc, sử dụng minimax
    best_move = None
    best_eval = -math.inf
    moves = generate_legal_moves(board, color)
    for piece, move in moves:
        board.make_move(piece, move)
        eval = minimax(board, depth-1, -math.inf, math.inf, False, color)
        board.undo_move()
        if eval > best_eval:
            best_eval = eval
            best_move = (piece, move)
    if best_move:
        return best_move[1]
    return None 