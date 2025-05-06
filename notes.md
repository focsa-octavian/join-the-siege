# Heron Coding Challenge - File Classifier - Octavian Focsa - Notes - 3rd May 2025

- `python3 -m venv venv`
- `source venv/bin/activate`
-  `pip install -r requirements.txt`

- Run Flask app
- `python -m src.app`

- test each of the files manually
- all fine but note that there is a small catch between "licence" vs "license"
- british {noun} vs american {noun, verb}
- and it is consistent wrt to the context of the licences also

- so the first small improvement would be to check across spelling variations
- added

- this is a valid variation, however, it might be good to try to take care of minor misspleeing in general
- note, could also think of trying to include some regex here which could do the same job or similar, but would probably be a bit convoluted and overkill...
- quick scan have found a pyhton lib pyspellchecker, looks pretty good for my needs

- `pip install pyspellchecker`

- simple iteration added on top of base case where the file_basename is split by "_" and each word is corrected
- occuring to me now that of course a filename might be joined by other charachters, eg. "-", but will gloss over this for today...

- next iteration would be to try to extract the text from the files and to classify the files based on this text
- pypdf looks like a good condidate (for pdfs), let's try
- seems to work nicely

- now we have the option to do a sort of manual check, looking for words that you might expect to appear in a bank statement, or drivers licence etc.
- or we could pass it to a model which outputs likleihoods
- or both...

- have also found pytesseract for images, testing that quickly also
- pytesseract has some awkwardness related to including tesseract executable in your PATH
- which cause a little problem when trying to check in differnt environments or in prod...

- ssl certificate error I think because of tryong to download the model
- manually download it myself

- https://www.jaided.ai/easyocr/modelhub/
- english_g2.pth
- move to ~/.EasyOCR/model

- still the same problem...
- ok, so I think I had the wrong model wrt. the language I was specifying, 'en', was not obvious...
- 'en': 'craft_mlt_25k.pth'
- ok, so maybe actually you need both...
- yup, this has finally worked...

- so stick with this method and uninstall pytesseract
- so we now have models which work with both pdfs and images in general

- `pip install pypdf`
- `pip install easyocr`
- from https://www.jaided.ai/easyocr/modelhub/ download both `english_g2` and `CRAFT` and move to `~/.EasyOCR/model/
- resulting with
- `ls ~/.EasyOCR/model/`
- Output: craft_mlt_25k.pth       english_g2.pth

- `pip install numpy` already satisfied
- `pip install torch` already satisfied
- `pip install transformers`

- Text Classification
- `from transformers import pipeline`
- `classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')`
- `labels = ['bank statement', 'drivers licence', 'invoice']`
-  `hypothesis_template = 'This text is about {}.'`
- ` sequence = "Bank Statement Example"`
- `prediction = classifier(sequence, labels, hypothesis_template=hypothesis_template, multi_label=False)`

- I wanted to add some tests also for the new classification functions against the exisiting files but I had yet to account for some edge-cases...

# TODO
- implement testing for each of the cases
- potentially refactor the code in order to logically separate
- think about the order of escalation in terms of the steps the clasification goes through
- think of edge cases
- try-catch clauses so that the server does't crash
- containerise app to make sure it should work in any environment inc prod
- the classification seems to works super fast on each level, but thinking about scaling up
- could implement a message queue and listener
- can think of ways to expand classes, either manually or by some other technique
- could try to automate this also...
- write a small bash script to automatically download, unzip and move the EasyOCR models as described above
- https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip
- https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip
- 
