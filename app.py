import os
import shutil
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

import subprocess

app = FastAPI()

# Email myself on this hit and log (through azure most likely)
@app.post("/uploadfiles/")
async def create_upload_files(file: UploadFile = File(...)):
    upload_folder = 'ready/'
    file_object = file.file
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    # TODO: Just mount the pretrained model
    subprocess.call(['python -m demucs.separate {}ready/{} --dl -n demucs_extra -d cpu'.format(os.getcwd(), file.filename)], shell=True)
    return "Shredded {}".format(file.filename)


@app.get("/dev")
async def main():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)