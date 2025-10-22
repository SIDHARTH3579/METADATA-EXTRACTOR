from PIL import Image
import exifread
import PyPDF2
import docx
from mutagen import File as AudioFile
import filetype
import io
import os
from typing import Tuple


def detect_file_type(file_path: str) -> str:
    kind = filetype.guess(file_path)
    if kind:
        return f"{kind.mime} ({kind.extension})"
    else:
        return "Unknown / Unsupported"


def extract_metadata(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    metadata = {}

    try:
        if ext in ['.jpg', '.jpeg', '.png']:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                metadata = {k: str(v) for k, v in tags.items()}

        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                metadata = dict(reader.metadata) if reader.metadata else {}

        elif ext == '.docx':
            doc = docx.Document(file_path)
            props = doc.core_properties
            metadata = {
                'author': props.author,
                'title': props.title,
                'subject': props.subject,
                'created': str(props.created),
                'modified': str(props.modified),
            }

        elif ext in ['.mp3', '.flac', '.wav', '.ogg']:
            audio = AudioFile(file_path)
            metadata = {k: str(v) for k, v in audio.tags.items()} if audio.tags else {}

        else:
            metadata = {"info": "Unsupported file type or no metadata found"}

    except Exception as e:
        metadata = {"error": str(e)}

    return metadata


def strip_metadata(file_path: str) -> Tuple[bytes, str]:
    ext = os.path.splitext(file_path)[1].lower()
    buffer = io.BytesIO()

    try:
        if ext in ['.jpg', '.jpeg', '.png']:
            image = Image.open(file_path)
            clean_image = Image.new(image.mode, image.size)
            clean_image.putdata(list(image.getdata()))
            clean_image.save(buffer, format=image.format)
            buffer.seek(0)

        elif ext == '.pdf':
            reader = PyPDF2.PdfReader(file_path)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.remove_metadata()
            writer.write(buffer)
            buffer.seek(0)

        elif ext == '.docx':
            doc = docx.Document(file_path)
            props = doc.core_properties
            props.author = None
            props.title = None
            props.subject = None
            props.created = None
            props.modified = None
            doc.save(buffer)
            buffer.seek(0)

        elif ext in ['.mp3', '.flac', '.wav', '.ogg']:
            audio = AudioFile(file_path)
            audio.delete()
            audio.save()
            with open(file_path, 'rb') as f:
                buffer.write(f.read())
            buffer.seek(0)

        else:
            raise ValueError("Unsupported file type for cleaning")

    except Exception as e:
        return bytes(str(e), 'utf-8'), "txt"

    return buffer.getvalue(), ext
