from werkzeug.datastructures import FileStorage

from spellchecker import SpellChecker

spell = SpellChecker()


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

    return "unknown file"

