# Chess AI

Một ứng dụng cờ vua với AI được phát triển bằng Python, sử dụng thuật toán Minimax với Alpha-Beta Pruning.

## Tính năng chính

### 1. Giao diện người dùng
- Giao diện đồ họa sử dụng Pygame
- Hỗ trợ kéo thả quân cờ
- Hiển thị các nước đi hợp lệ
- Hiệu ứng âm thanh khi di chuyển quân

### 2. AI thông minh
- Sử dụng thuật toán Minimax với Alpha-Beta Pruning
- Độ sâu tìm kiếm có thể điều chỉnh (Độ sâu max hiện tại đang thử nghiệm là 4)
- Đánh giá bàn cờ đa chiều:
  - Giá trị quân cờ
  - Vị trí quân cờ (position tables)
  - Cấu trúc tốt (pawn structure)
  - Bảo vệ vua
  - Kiểm soát trung tâm
  - Phát triển quân

### 3. Khai cuộc
- Hỗ trợ khai cuộc Sicilian Defense
- Tự động chuyển sang minimax khi khai cuộc bị phá vỡ
- Kiểm tra và bảo vệ các quân trong khai cuộc

### 4. Luật chơi
- Tuân thủ đầy đủ luật cờ vua quốc tế
- Hỗ trợ:
  - Bắt tốt qua đường (En Passant)
  - Nhập thành (Castling)
  - Phong cấp tốt
  - Chiếu hết
  - Hòa cờ

## Cài đặt

1. Yêu cầu hệ thống:
   - Python 3.7 trở lên
   - Pygame

2. Cài đặt các thư viện:
```bash
pip install pygame
```

3. Chạy game:
```bash
python main.py
```

## Cấu trúc dự án

```
Chess_AI/
├── main.py           # File chính để chạy game
├── game.py          # Quản lý logic game
├── board.py         # Quản lý bàn cờ và luật chơi
├── ai.py            # AI và thuật toán đánh giá
├── piece.py         # Định nghĩa các quân cờ
├── square.py        # Định nghĩa ô cờ
├── move.py          # Định nghĩa nước đi
├── ui.py            # Giao diện người dùng
├── dragger.py       # Xử lý kéo thả
├── sound.py         # Xử lý âm thanh
├── const.py         # Các hằng số
├── settings.py      # Cài đặt game
└── assets/          # Thư mục chứa hình ảnh và âm thanh
```

## Tùy chỉnh AI

Có thể điều chỉnh các thông số AI trong file `ai.py`:
- Độ sâu tìm kiếm
- Hệ số đánh giá
- Bảng điểm vị trí
- Cấu trúc khai cuộc
