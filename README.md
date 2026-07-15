# Audio Converter

Công cụ Python chuyển nội dung tài liệu thành file âm thanh MP3 tiếng Việt bằng
dịch vụ Microsoft Edge Text-to-Speech (`edge-tts`).

Chương trình hỗ trợ đọc tài liệu Markdown, PDF và văn bản thuần, làm sạch nội
dung, chia văn bản thành nhiều phần nhỏ, tạo âm thanh cho từng phần rồi ghép
thành một file MP3 hoàn chỉnh.

## Tính năng

- Hỗ trợ file `.md`, `.pdf` và `.txt`.
- Đọc tiếng Việt với giọng mặc định `vi-VN-HoaiMyNeural`.
- Làm sạch lỗi xuống dòng và từ bị ngắt bởi dấu gạch nối trong PDF.
- Chuyển bảng Markdown thành câu văn phù hợp để đọc thành tiếng.
- Tự động chia tài liệu dài thành các phần nhỏ.
- Thử lại tối đa 3 lần khi tải một phần âm thanh thất bại.
- Lưu kết quả theo ngày trong thư mục `mp3/YYYY-MM-DD/`.

## Yêu cầu

- Python 3.10 trở lên.
- Kết nối Internet để sử dụng dịch vụ `edge-tts`.
- `pip` và môi trường ảo Python.

## Cài đặt

Sao chép dự án:

```bash
git clone <URL_REPOSITORY>
cd audio-converter
```

Tạo và kích hoạt môi trường ảo:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Trên Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Cài đặt thư viện:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Tạo file cấu hình môi trường từ file mẫu:

```bash
cp .env.example .env
```

Trên Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## Cách sử dụng

### 1. Chuẩn bị tài liệu

Tạo thư mục `sources` và đặt tài liệu cần chuyển đổi vào đó:

```text
sources/
├── tai-lieu.txt
├── ghi-chu.md
└── sach.pdf
```

Thư mục `sources` không được đưa lên GitHub vì đã được khai báo trong
`.gitignore`.

### 2. Chuyển tài liệu thành MP3

```bash
python audio_converter.py sources/tai-lieu.txt
```

Ví dụ với Markdown hoặc PDF:

```bash
python audio_converter.py sources/ghi-chu.md
python audio_converter.py sources/sach.pdf
```

File kết quả được tạo theo cấu trúc:

```text
mp3/
└── YYYY-MM-DD/
    └── ten-tai-lieu.mp3
```

Ví dụ:

```text
mp3/2026-07-15/tai-lieu.mp3
```

### 3. Kiểm tra nội dung được đọc từ tài liệu

Có thể xem trước văn bản trích xuất mà không tạo file âm thanh:

```bash
python document_reader.py sources/sach.pdf
```

## Cấu hình

Các thiết lập nằm trong file `.env`. Có thể sao chép và chỉnh sửa từ
`.env.example`:

```dotenv
VOICE=vi-VN-HoaiMyNeural
RATE=+10%
CHUNK_SIZE=1500
TEMP_DIR=temp_chunks
OUTPUT_DIR=mp3
```

- `VOICE`: giọng đọc của Edge TTS.
- `RATE`: tốc độ đọc; dùng giá trị âm để đọc chậm hơn.
- `CHUNK_SIZE`: số ký tự tối đa dự kiến trong mỗi phần.
- `TEMP_DIR`: nơi lưu tạm các phần âm thanh.
- `OUTPUT_DIR`: thư mục chứa file MP3 hoàn chỉnh.

## Cấu trúc dự án

```text
audio-converter/
├── audio_converter.py   # Điều phối việc chia nội dung, tạo và ghép MP3
├── document_reader.py   # Đọc file Markdown, PDF và văn bản thuần
├── line_joiner.py       # Làm sạch cấu trúc văn bản trích xuất từ PDF
├── markdown_speech.py   # Chuyển Markdown thành nội dung phù hợp cho TTS
├── requirements.txt     # Danh sách thư viện Python
├── sources/             # Tài liệu đầu vào, không đưa lên Git
├── mp3/                 # File âm thanh đầu ra, không đưa lên Git
├── .env.example         # Cấu hình môi trường mẫu
├── .gitignore
├── LICENSE
└── README.md
```

Trong lúc chạy, chương trình tạo thư mục `temp_chunks` để lưu các file MP3 tạm
thời và xóa thư mục này sau khi ghép thành công.

## Quy trình xử lý

1. Kiểm tra file đầu vào và định dạng được hỗ trợ.
2. Đọc nội dung tài liệu.
3. Làm sạch nội dung PDF hoặc chuyển đổi cấu trúc Markdown.
4. Chia văn bản thành các phần nhỏ theo dấu kết thúc câu.
5. Gửi từng phần tới dịch vụ Edge TTS.
6. Ghép các phần âm thanh thành một file MP3.
7. Lưu file kết quả vào thư mục theo ngày.

## Xử lý lỗi thường gặp

### Không tìm thấy file đầu vào

Kiểm tra lại đường dẫn và tên file:

```bash
ls sources
```

### Định dạng không được hỗ trợ

Chương trình chỉ hỗ trợ `.md`, `.pdf` và `.txt`.

### Không tải được âm thanh

Kiểm tra kết nối Internet rồi chạy lại lệnh. Chương trình tự thử lại mỗi phần
tối đa 3 lần trước khi dừng.

### PDF không có nội dung

Một số PDF chỉ chứa hình ảnh được quét và không có lớp văn bản. Phiên bản hiện
tại chưa hỗ trợ OCR cho loại tài liệu này.

## Giấy phép

Dự án được phát hành theo giấy phép MIT. Xem file [LICENSE](LICENSE) để biết
thêm chi tiết.
