from werkzeug.datastructures import FileStorage
import io

from spellchecker import SpellChecker
from pypdf import PdfReader
import easyocr
from transformers import pipeline


spell = SpellChecker()
ocr_reader = easyocr.Reader(['en']) # model_storage_directory='~/.EasyOCR/model/', download_enabled=False
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

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

def get_sequence(words):
    return " ".join(words)

def get_text_classification(words):

    SCORE_THRESHOLD = 0.6 # e.g.

    labels = ['bank statement', 'drivers licence', 'invoice']
    # labels = ['bank statement', 'drivers licence', 'invoice', 'miscellaneous']
    # labels = ['bank statement', 'drivers licence', 'invoice', 'not bank statement', 'not drivers licence', 'not invoice'] # w/ multi_label=True
    hypothesis_template = 'This text is about {}.'
    sequence = get_sequence(words)

    prediction = classifier(sequence, labels, hypothesis_template=hypothesis_template, multi_label=False)
    label = prediction['labels'][0]
    score = prediction['scores'][0]

    if score < SCORE_THRESHOLD:
        return None
    
    if label == "drivers licence":
        return "drivers_licence"
    elif label == "bank statement":
        return "bank_statement"
    elif label == "invoice":
        return "invoice"

    return None


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

    if set(["driving", "driver"]).intersection(words) and set(["licence", "license"]).intersection(words):
        return "drivers_licence"

    if set(['bank', 'statement']) <= set(words):
        return "bank_statement"

    if "invoice" in words:
        return "invoice"
    
    # 3 Text Classifier

    text_classification = get_text_classification(words)

    if text_classification:
        return text_classification

    return "unknown file"

