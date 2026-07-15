import re

def clean_pdf_text_structure(text):
    """
    Xử lý lỗi xuống dòng vô tội vạ và từ bị cắt đôi từ file PDF.
    """
    # Bước a: Ghép các từ bị bẻ đôi ở cuối dòng do dấu gạch nối (e.g., "de-\nveloper" -> "developer")
    text = re.sub(
        r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)',
        '',
        text,
    )

    # Bước b: Nối các dòng bị ngắt ngẫu nhiên trong PDF
    lines = text.split('\n')
    cleaned_lines = []
    temp_paragraph = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            # Nếu gặp dòng trống, nghĩa là kết thúc một đoạn văn thực sự
            if temp_paragraph:
                cleaned_lines.append(" ".join(temp_paragraph))
                temp_paragraph = []
            cleaned_lines.append("") # Giữ lại dòng trống để tạo ngắt nghỉ dài hơn
            continue

        temp_paragraph.append(line_str)

        # Kiểm tra xem dòng hiện tại có dấu hiệu kết thúc một câu hoàn chỉnh không
        # Nếu kết thúc bằng dấu câu (. ! ? :) hoặc dấu ngoặc kép, dấu ngoặc đơn thì đóng đoạn để đọc ngắt nghỉ
        if re.search(r'[.!?:]\s*$', line_str):
            cleaned_lines.append(" ".join(temp_paragraph))
            temp_paragraph = []

    if temp_paragraph:
        cleaned_lines.append(" ".join(temp_paragraph))

    # Gộp các dòng đã làm sạch lại với nhau
    processed_text = "\n".join(cleaned_lines)
    
    # Loại bỏ các khoảng trắng thừa do quá trình nối dòng sinh ra
    processed_text = re.sub(r' +', ' ', processed_text)
    return processed_text
