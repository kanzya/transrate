import requests
import pprint
import urllib
import json
import shutil
from tqdm import tqdm
from deepl import deepl
import glob
import os
from PyPDF2 import PdfWriter, PdfReader


def init():
    shutil.rmtree('./translated/alt')
    shutil.rmtree('./translated/ja')
    shutil.rmtree('./translated/list')

    os.mkdir('./translated/alt')
    os.mkdir('./translated/ja')
    os.mkdir('./translated/list')


def split():
    for file_name in glob.glob('*.pdf'):
        (name, extention) = os.path.splitext(file_name)
        pdf_file_reader = PdfReader(file_name)
        page_nums = len(pdf_file_reader.pages)
        print(page_nums)

    for num in range(page_nums):
        file_object = pdf_file_reader.pages[num]
        pdf_file_name = f"nowing-{str(num + 1).zfill(3)}.pdf"
        pdf_file_writer = PdfWriter()
        with open("./translated/list/" + pdf_file_name, 'wb') as f:
            pdf_file_writer.add_page(file_object)
            pdf_file_writer.write(f)
    return name, page_nums


def conbine(name, path):
    from pathlib import Path

    pdf_dir = Path("./translated/" + path)
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if path == "alt":
        pdf_files = sorted(Path("./translated/").glob("*.pdf.1")) + pdf_files
    pdf_writer = PdfWriter()
    for pdf_file in pdf_files:
        pdf_reader = PdfReader(str(pdf_file))
        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.pages[i])

    merged_file = name + path + ".pdf"
    with open(merged_file, "wb") as f:
        pdf_writer.write(f)


def send_first(FILE_NAME):
    URL = "https://api.readable.jp/toquery/"
    test_file = open("./translated/list/" + FILE_NAME, "rb")
    test_response = requests.post(URL, files={"file": test_file})
    DEEPL_URL = test_response.json()["url"]
    UUID = test_response.json()["uuid"]
    return DEEPL_URL, UUID


def DEEPL2(texts):
    texts = urllib.parse.unquote(texts).replace("https://www.deepl.com/translator#en/ja/", "")
    t = deepl.DeepLCLI("en", "ja", timeout=15000 * 3)
    rets = [t.translate(text) for text in texts.split("\n------------------------------\n")[:-1]]
    rets = "\n------------------------------\n".join(rets) + "\n------------------------------\n"
    return rets


def send_transrate(translate, UUID, filename):
    print("SENDED")
    URL = "https://api.readable.jp/generate/"
    response = requests.post(URL, json.dumps({'uuid': UUID, 'body': translate, 'original_filename': filename}), headers={'Content-Type': 'application/json'})
    pprint.pprint(response.json())
    jp = response.json()["ja"]
    alt = response.json()["alt"]
    print(jp, alt)
    return jp, alt


def wget_file(NAME, URL, TYPE):

    url = "https://files.readable.jp/" + URL
    print(url)
    urlData = requests.get(url).content
    open("./translated/" + TYPE + "/" + NAME, mode='wb').write(urlData)


init()
ORG_NAME, page = split()

for p in tqdm(range(page)):
    file_name = "nowing-" + str(p + 1).zfill(3) + ".pdf"
    URL, UUID = send_first(file_name)
    translate = DEEPL2(URL)
    NAME_JA, NAME_ALT = send_transrate(translate, UUID, file_name)
    wget_file(file_name, NAME_ALT, "alt")
    wget_file(file_name, NAME_JA, "ja")

conbine(ORG_NAME, "ja")
conbine(ORG_NAME, "alt")
print("fin transrate")
