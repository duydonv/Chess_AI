import os
import pygame

class Piece:
    # Cache cho texture
    _texture_cache = {}
    
    def __init__(self, name, color, texture = None, texture_react = None):
        self.name = name
        self.color = color
        self.moves = []
        self.moved = False
        self.texture = texture
        self.set_texture()
        self.texture_react = texture_react

    def set_texture(self, size = 70):
        self.texture = os.path.join(
            f'assets/images/imgs-{size}px/{self.color}_{self.name}.png'
        )
        
        # Cache texture
        if self.texture not in self._texture_cache:
            self._texture_cache[self.texture] = pygame.image.load(self.texture)

    def add_move(self, move):
        self.moves.append(move)
    
    def clear_moves(self):
        self.moves = []

    @classmethod
    def clear_texture_cache(cls):
        cls._texture_cache.clear()

# định nghĩa các quân tốt
class Pawn(Piece):

    def __init__(self, color):
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False
        super().__init__('pawn', color)
# định nghĩa các quân mã
class Knight(Piece):

    def __init__(self, color):
        super().__init__('knight', color)
# định nghĩa các quân tượng
class Bishop(Piece):
    
    def __init__(self, color):
        super().__init__('bishop', color)
# định nghĩa các quân xe
class Rook(Piece):
    
    def __init__(self, color):
        super().__init__('rook', color)
# định nghĩa các quân hậu
class Queen(Piece):
    
    def __init__(self, color):
        super().__init__('queen', color)
# định nghĩa các quân vua
class King(Piece):
    
    def __init__(self, color):
        super().__init__('king', color)