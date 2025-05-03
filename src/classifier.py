from werkzeug.datastructures import FileStorage
import io

from spellchecker import SpellChecker
from pypdf import PdfReader
import easyocr


spell = SpellChecker()
ocr_reader = easyocr.Reader(['en']) # model_storage_directory='~/.EasyOCR/model/', download_enabled=False

def base(filename):
    if "drivers_license" in filename or "drivers_licence" in filename:
        return "drivers_licence"

    if "bank_statement" in filename:
        return "bank_statement"

    if "invoice" in filename:
        return "invoice"
    
    return None

def get_spellcheck(filename):
    file_basename = filename.rsplit('.', 1)[0].lower()
    file_basename_list = file_basename.split("_")
    file_basename_correction = "_".join([spell.correction(word) for word in file_basename_list])
    return file_basename_correction

def get_words(file):

    filename = file.filename.lower()
    extension = filename.rsplit('.', 1)[1].lower()

    if extension == "pdf":
        reader = PdfReader(file)
        words = []

        for page in reader.pages:
            text_page = page.extract_text()
            words_per_line_per_page = [line.split(" ") for line in text_page.split("\n")]
            for line in words_per_line_per_page:
                for word in line:
                    words.append(word.lower())

        return words

    elif extension in ["png", "jpg"]:
        result = ocr_reader.readtext(file.read())
        words_raw = [word[-2].split(" ") for word in result]
        words = [word.lower() for innerList in words_raw for word in innerList]
        
        return words

    return []

def classify_file(file: FileStorage):
    filename = file.filename.lower()
    # file_bytes = file.read()

    # 0 Base
    
    result = base(filename)

    if result:
        return result
    
    # 1 Base w/ spell check
    
    file_basename_correction = get_spellcheck(filename)
    result = base(file_basename_correction)

    if result:
        return result
    
    # 2 PDF Reader & OCR

    words = get_words(file)

    if set(['bank', 'statement']) <= set(words):
        return "bank_statement"
    
    if set(["driving", "driver"]).intersection(words) and set(["licence", "license"]).intersection(words):
        return "drivers_licence"

    if "invoice" in words:
        return "invoice"

    return "unknown file"

