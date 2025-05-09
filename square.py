
class Square:

    def __init__(self, row, col, piece = None, promotion_piece = None):
        self.row = row
        self.col = col
        self.piece = piece
        self.promotion_piece = promotion_piece

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def has_piece(self):
        return self.piece != None
    
    def has_promotion_piece(self):
        return self.promotion_piece is not None
    
    def isempty(self):
        return not self.has_piece()
    
    def has_team_piece(self, color):
        return self.has_piece() and self.piece.color == color
    
    def has_enemy_piece(self, color):
        return self.has_piece() and self.piece.color != color

    def isempty_or_enemy(self, color):
        return self.isempty() or self.has_enemy_piece(color)
    
    # Phương thức static ko cần khởi tạo đối tượng mà vẫn gọi được
    @staticmethod
    # Phương thức in_range kiểm tra xem ô có thuộc bàn cờ hay không
    def in_range(*args):
        for arg in args:
            if arg < 0 or arg > 7:
                return False
            
        return True