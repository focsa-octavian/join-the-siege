from io import BytesIO
import os
import random

import pytest
from src.app import app, allowed_file

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("filename, expected", [
    ("file.pdf", True),
    ("file.png", True),
    ("file.jpg", True),
    ("file.txt", False),
    ("file", False),
])
def test_allowed_file(filename, expected):
    assert allowed_file(filename) == expected

def test_no_file_in_request(client):
    response = client.post('/classify_file')
    assert response.status_code == 400

def test_no_selected_file(client):
    data = {'file': (BytesIO(b""), '')}  # Empty filename
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

def test_success(client, mocker):
    mocker.patch('src.app.classify_file', return_value='test_class')

    data = {'file': (BytesIO(b"dummy content"), 'file.pdf')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json() == {"file_class": "test_class"}

# @pytest.mark.parametrize("filename, classification", [
#     ("bank_statement_1.pdf", "bank_statement"),
#     ("bank_statement_2.pdf", "bank_statement"),
#     ("bank_statement_3.pdf", "bank_statement"),
#     ("drivers_license_1.jpg", "drivers_licence"),
#     ("drivers_licence_2.jpg", "drivers_licence"),
#     ("drivers_license_3.jpg", "drivers_licence"),
#     ("invoice_1.pdf", "invoice"),
#     ("invoice_2.pdf", "invoice"),
#     ("invoice_3.pdf", "invoice"),
# ])
# def test_base_w_spellcheck(client, filename, classification):

#     dir = "files"
#     filepath = os.path.join(dir, filename)
    
#     with open(filepath, 'rb') as fh:
#         file = BytesIO(fh.read())

#     # basename, extension = filename.split(".")
#     # idx = random.randint(0, len(basename) - 1)
#     # basename = basename[:idx] + "_" + basename[idx+1:]
#     # filename = str(".".join([basename, extension]))

#     data = {'file': (file, filename)}
#     response = client.post('/classify_file', data=data, content_type='multipart/form-data')
#     assert response.status_code == 200
#     assert response.get_json() == {"file_class": classification}

# @pytest.mark.parametrize("filename, classification", [
#     ("bank_statement_1.pdf", "bank_statement"),
#     ("bank_statement_2.pdf", "bank_statement"),
#     ("bank_statement_3.pdf", "bank_statement"),
#     ("drivers_license_1.jpg", "drivers_licence"),
#     ("drivers_licence_2.jpg", "drivers_licence"),
#     ("drivers_license_3.jpg", "drivers_licence"),
#     ("invoice_1.pdf", "invoice"),
#     ("invoice_2.pdf", "invoice"),
#     ("invoice_3.pdf", "unknown file"),
# ])
# def test_(client, filename, classification):

#     dir = "files"
#     filepath = os.path.join(dir, filename)
    
#     with open(filepath, 'rb') as fh:
#         file = BytesIO(fh.read())

#     extension = filename.split(".")[-1]
#     filename = "test" + extension

#     data = {'file': (file, filename)}
#     response = client.post('/classify_file', data=data, content_type='multipart/form-data')
#     assert response.status_code == 200
#     assert response.get_json() == {"file_class": classification}
