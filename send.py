import requests
import pprint
import urllib
import json
import shutil
from tqdm import tqdm

from deepl import deepl

import glob,os 
from PyPDF2 import PdfFileWriter, PdfFileReader

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
        pdf_file_reader = PdfFileReader(file_name)
        page_nums = pdf_file_reader.getNumPages()
        print(page_nums)

    for num in range(page_nums):
        file_object = pdf_file_reader.getPage(num)
        pdf_file_name = "nowing" + '-' + str(num+1).zfill(3) + '.pdf'
        pdf_file_writer = PdfFileWriter()
        with open("./translated/list/"+pdf_file_name,'wb') as f: 
            pdf_file_writer.addPage(file_object) 
            pdf_file_writer.write(f) 
    return name ,page_nums

def conbine(name,path):
    from pathlib import Path

    pdf_dir = Path("./translated/"+path)
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if path=="alt":
        pdf_files =sorted(Path("./translated/").glob("*.pdf.1"))+pdf_files
    pdf_writer = PdfFileWriter()
    for pdf_file in pdf_files:
        pdf_reader = PdfFileReader(str(pdf_file))
        for i in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(i))

    merged_file = name +path+".pdf"
    with open(merged_file, "wb") as f:
        pdf_writer.write(f)

def send_first(FILE_NAME):
    URL = "https://readable.jp/api/toquery/"
    test_file = open("./translated/list/"+FILE_NAME, "rb")
    test_response = requests.post(URL, data={'name': 'file','filename': FILE_NAME} ,files = {"file": test_file})
    # print(test_response)
    # print(test_response.json(),FILE_NAME)
    DEEPL_URL = test_response.json()["url"]
    UUID = test_response.json()["uuid"]
    return DEEPL_URL , UUID

def DEEPL(text):
    import json
    # print(urllib.parse.unquote(text).replace("https://www.deepl.com/translator#en/ja/",""))
    text = urllib.parse.unquote(text).replace("https://www.deepl.com/translator#en/ja/","")

    API_KEY = '' # 自身の API キーを指定

    source_lang = 'EN'
    target_lang = 'JA'

    # パラメータの指定
    params = {
                'auth_key' : API_KEY,
                'text' : text,
                'source_lang' : source_lang, # 翻訳対象の言語
                "target_lang": target_lang  # 翻訳後の言語
            }

    # リクエストを投げる
    request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
    result = request.json()
    # print(type(result))
    # json_object = json.load(result)
    print(result)
    # print( type(result["translations"]))
    # print( result["translations"])
    return str(result["translations"]).replace("\\n","\n").replace("[{'detected_source_language': 'EN', 'text': '","")[:-3] + "\n\nwww.DeepL.com/Translator（無料版）で翻訳しました。"

def DEEPL2(text):
    text = urllib.parse.unquote(text).replace("https://www.deepl.com/translator#en/ja/","")
    # print(text)
    t = deepl.DeepLCLI("en", "ja")
    ret = t.translate(text) #=> "こんにちわ"
    # print(ret)
    return ret

def send_options():
    URL =  "https://readable.jp/api/generate/"
    result = requests.options(URL,headers={"Host": "tmp.joisino.net",
                                           "Accept": "*/*","Access-Control-Request-Method": "POST",
                                           "Access-Control-Request-Headers": "content-type",
                                           "Origin": "https://readable.joisino.net",
                                           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                                           "Sec-Fetch-Mode": "cors",
                                           "Sec-Fetch-Site": "same-site",
                                           "Sec-Fetch-Dest": "empty",
                                           "Referer": "https://readable.joisino.net/",
                                           "Accept-Encoding": "gzip, deflate",
                                           "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
                                           "Connection": "close"})
    print(result)
    pprint.pprint(result.text)   

def send_transrate(translate,UUID):
    URL = "https://readable.jp/api/generate/"
    response = requests.post(URL,json.dumps({'uuid': UUID,'body': translate}),headers={'Content-Type': 'application/json'})
    pprint.pprint(response.json())
    jp = response.json()["ja"]
    alt = response.json()["alt"]
    print(jp,alt)    
    return jp ,alt

def wget_file(NAME,URL,TYPE):
    
    url="https://readable.jp/"+URL
    urlData = requests.get(url).content
    with open("./translated/"+TYPE+"/"+NAME ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
        


init()
ORG_NAME,page = split()
print(ORG_NAME,page)

for p in tqdm(range(page)):
    file_name = "nowing-"+str(p+1).zfill(3)+".pdf"
    # print(file_name)
    URL ,UUID = send_first(file_name)
    # translate = DEEPL(URL)
    translate = DEEPL2(URL)
    # print()
    # print(translate)
    NAME_JA ,NAME_ALT = send_transrate(translate,UUID)
    wget_file(file_name,NAME_ALT,"alt")
    wget_file(file_name,NAME_JA,"ja")

conbine(ORG_NAME,"ja")
conbine(ORG_NAME,"alt")
print("fin transrate")