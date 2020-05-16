import os.path
import io
from googleapiclient.http import MediaIoBaseDownload


def download_dir(service, file_id, out, nome, nvl):

    target = os.path.join(out, nome)

    while os.path.exists(target):

        target += "_"

    os.mkdir(target)

    results = service.files().list(q=f"'{file_id}' in parents").execute()
    items = results.get('files', [])


    for item in items:

        file_id = item['id']
        nome = item['name']
        tipo = item['mimeType']

        download_by_file_id(service,file_id, target, nome, tipo, nvl)




def download_file(service, file_id, out, nome):



    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


    open(os.path.join(out, nome), 'wb').write(fh.getbuffer())



def download_google_doc(service, file_id, out, nome, tipo, ext):

    request = service.files().export_media(fileId=file_id,
                                                 mimeType=tipo)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    open(os.path.join(out, nome+ext), 'wb').write(fh.getbuffer())





def download_by_file_id(service, file_id, out, nome, tipo, nvl):


    if file_id == 'root': nome = 'root'

    if tipo == 'application/vnd.google-apps.folder' or file_id == 'root':

        print("  " * nvl, nome+'/')
        download_dir(service, file_id, out, nome, nvl+1)


    elif "vnd.google-apps" in tipo:

        print("  " * nvl, nome)
        l = {
            "document" : ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", '.docx'],
            "spreadsheet" : ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", '.xlxs']
        }

        tipo = tipo.split('.')[-1]

        if tipo in l:

            download_google_doc(service, file_id, out, nome, *l[tipo])

        else: print("Não foi possível baixar arquivo", nome)

    else:
        print("  " * nvl, nome)
        download_file(service, file_id, out, nome)

def download(service, filepath="", out = ''):

    if filepath == '.': filepath = ''

    if out != '' and not os.path.exists(out):

        print(" Err : Caminho de saída inválido")
        return

    if filepath: path = filepath.split("/")
    else: path = ""

    diretorio_pai = 'root'

    nome = ''

    tipo = ''



    while path:

        chave = path[0]
        path = path[1:]

        results = service.files().list(q=f"name contains '{chave}' and '{diretorio_pai}' in parents").execute()
        items = results.get('files', [])

        if not items:
            print('Err : Arquivo não encontrado')
            return
        else:


            diretorio_pai = items[0]['id']
            nome = items[0]['name']
            tipo = items[0]['mimeType']



    if not path: download_by_file_id(service, diretorio_pai, out, nome, tipo, 0)