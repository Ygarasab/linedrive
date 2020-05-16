import os.path as path
import os
from uploader.mimedict import mimedict
from googleapiclient.http import MediaFileUpload

def upload_file(service, file_path, parent_id):

    print(parent_id)

    while "\\" in file_path:

        file_path = file_path.replace("\\","/")

    nome = file_path.split("/")[-1]

    ext = nome.split(".")[-1]

    mime = mimedict[ext] if ext in mimedict.keys() else "text/plain"

    metadados = {
        'name' : nome,
        'parents' : [parent_id]
    }

    media = MediaFileUpload(file_path, mimetype=mime)

    file = service.files().create(body=metadados,
                                        media_body=media,
                                        fields='id').execute()



def upload_folder(service, parent_id, file_path, nvl):



    while "\\" in file_path:

        file_path = file_path.replace("\\","/")

    chave = file_path.split("/")[-1]

    print("Adicionando folder", file_path, chave)

    results = service.files().list(q=f"name = '{chave}' and '{parent_id}' in parents and trashed = false").execute()
    items = results.get('files', [])

    if not items:

        print("criando", chave)

        file_metadata = {
            'name': chave,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = service.files().create(body=file_metadata,
                                            fields='id').execute()

        id = file.get('id')

    else:

        id = items[0]['id']


    for filho in os.listdir(file_path):

        print(id)

        upload_file_with_id(service,id, path.join(file_path, filho), nvl + 1)

def upload_file_with_id(service, parent_id, file_path, nvl):

    while "\\" in file_path:

        file_path = file_path.replace("\\","/")

    print("  " * nvl, file_path.split("/")[-1])

    if path.isdir(file_path):

        upload_folder(service, parent_id, file_path, nvl)

    else:

        upload_file(service,file_path,parent_id)


def upload(service, file_path = ".", out = ''):

    while '\\' in out:

        out.replace('\\', '/')

    if not path.exists(file_path):

        print("Err : Não foi possível acessar", file_path)
        return

    file_path = path.abspath(file_path)

    while '\\' in file_path:
        file_path = file_path.replace('\\', '/')

    if out: out = out.split("/")

    diretorio_pai = 'root'

    print("Carregando", file_path.split("/")[-1], "....")

    while out:

        chave = out[0]
        out = out[1:]

        results = service.files().list(q=f"name contains '{chave}' and '{diretorio_pai}' in parents").execute()

        items = results.get('files', [])

        if not items:

            print('Err : Caminho de saída inválido')
            return

        else:

            diretorio_pai = items[0]['id']

    if not out: upload_file_with_id(service, diretorio_pai, file_path, 0)


