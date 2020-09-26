import os
import shutil
from typing import List
from zipfile import ZipFile 

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse

import subprocess

app = FastAPI()

def get_all_file_paths(directory): 
    file_paths = [] 
    for root, directories, files in os.walk(directory): 
        for filename in files: 
            filepath = os.path.join(root, filename) 
            file_paths.append(filepath) 
    return file_paths  

# Email myself on this hit and log (through azure most likely)
@app.post("/uploadfiles/")
async def create_upload_files(file: UploadFile = File(...)):
    """"Entrypoint for source separation."""
    upload_folder = 'ready/'
    file_object = file.file
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    # TODO: Change to CUDA on Azure
    subprocess.call(['python -m demucs.separate {}/ready/{} --dl -n demucs_extra -d cpu'.format(os.getcwd(), file.filename)], shell=True)

    name = file.filename.replace('.mp3', '')
    
    file_paths = get_all_file_paths('separated/demucs_extra/{}'.format(name))

    with ZipFile('sources-{}.zip'.format(name),'w') as zip: 
        for file in file_paths: 
            zip.write(file) 

    return FileResponse('sources-{}.zip'.format(name), media_type='application/zip', filename='sources-{}.zip'.format(name))
    # Most likely want to delete / store these after (probably just delete)


@app.get("/dev")
async def main():
    """For local testing purposes only, the uploadfiles endpoint should be hit directly by a FA."""
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)