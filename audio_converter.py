import argparse
import os
import asyncio
import re
from datetime import date
import edge_tts
from dotenv import load_dotenv

from document_reader import prepare_speech_text, read_document_text


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Thiếu cấu hình bắt buộc trong file .env: {name}")
    return value


def clean_and_chunk_text(filepath, output_root, limit):
    raw_text = read_document_text(filepath)
    parsed_text = prepare_speech_text(filepath, raw_text)

    input_filename = os.path.basename(filepath)
    filename_without_extension = os.path.splitext(input_filename)[0]
    day_folder = date.today().strftime("%Y-%m-%d")
    output_dir = os.path.join(output_root, day_folder)
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(
        output_dir,
        f"{filename_without_extension}.mp3",
    )

    # Cắt chuỗi thông minh theo dấu câu
    sentences = re.split(r'(?<=[.!?])\s+', parsed_text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if current_length + len(sentence) > limit:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks, output_filename

async def download_chunk(index, text, voice, rate, temp_dir):
    temp_file_path = os.path.join(temp_dir, f"part_{index:04d}.mp3")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(temp_file_path)
    print(f" -> Đã hoàn thành phần {index + 1}")

async def main(input_file):
    print("=== KHỞI CHẠY HỆ THỐNG CHUYỂN VĂN BẢN THÀNH ÂM THANH ===")
    try:
        load_dotenv()
        voice = required_env("VOICE")
        rate = required_env("RATE")
        chunk_size = int(required_env("CHUNK_SIZE"))
        temp_dir = required_env("TEMP_DIR")
        output_dir = required_env("OUTPUT_DIR")

        chunks, output_filename = clean_and_chunk_text(
            input_file,
            output_dir,
            chunk_size,
        )
        total_chunks = len(chunks)
        print(f" Tác vụ: Đọc từ '{input_file}'")
        print(f" File đầu ra dự kiến: '{output_filename}'")
        print(f" Đã chia tài liệu thành {total_chunks} phần nhỏ để xử lý.")
    except Exception as e:
        print(f" LỖI KHỞI TẠO: Không thể xử lý file '{input_file}'. Lý do: {e}")
        return

    os.makedirs(temp_dir, exist_ok=True)

    print("\n--- BẮT ĐẦU DOWNLOAD CÁC PHÂN ĐOẠN ---")
    for i, chunk in enumerate(chunks):
        print(f" Đang tải phần {i+1}/{total_chunks} ({len(chunk)} ký tự)...")
        retry = 3
        while retry > 0:
            try:
                await download_chunk(i, chunk, voice, rate, temp_dir)
                break
            except Exception as ex:
                retry -= 1
                print(
                    f"   Lỗi tải phần {i + 1}/{total_chunks}: {ex}. "
                    f"Thử lại... (Còn {retry} lần thử)"
                )
                await asyncio.sleep(2)
        if retry == 0:
            print(" THẤT BẠI: Dừng tiến trình.")
            return

    print("\n--- TIẾN HÀNH GHÉP FILE AUDIO (BINARY MERGE) ---")
    try:
        chunk_files = sorted([f for f in os.listdir(temp_dir) if f.startswith("part_")])
        with open(output_filename, "wb") as outfile:
            for file_name in chunk_files:
                file_path = os.path.join(temp_dir, file_name)
                with open(file_path, "rb") as infile:
                    outfile.write(infile.read())
                os.remove(file_path)
        os.rmdir(temp_dir)
        print(f" THÀNH CÔNG RỰC RỠ! File: '{output_filename}'")
    except Exception as e:
        print(
            f" LỖI GHÉP FILE: Không thể tạo '{output_filename}'. "
            f"Lý do: {e}"
        )

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description="Chuyển file Markdown, PDF hoặc text thành MP3."
    )
    argument_parser.add_argument(
        "input_file",
        help="Đường dẫn file đầu vào (.md, .pdf hoặc .txt)",
    )
    arguments = argument_parser.parse_args()
    asyncio.run(main(arguments.input_file))