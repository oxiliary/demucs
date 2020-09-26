import os
import shutil
import subprocess
import random
from os.path import basename
from zipfile import ZipFile

from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()


def cleanup(file, name):
    """Remove files generated from request."""
    os.remove('sources-{}.zip'.format(file))
    os.remove('ready/{}'.format(file))
    shutil.rmtree('separated')


@app.post("/uploadfiles/")
async def create_upload_files(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """"Entrypoint for source separation."""
    name = file.filename
    file.filename = str(random.getrandbits(32))+'.mp3'
    upload_folder = open(os.path.join('ready/', file.filename), 'wb+')
    shutil.copyfileobj(file.file, upload_folder)
    upload_folder.close()
    subprocess.call(
        ['python -m demucs.separate {}/ready/{} --dl -n demucs_extra -d cpu'.format(os.getcwd(), file.filename)], shell=True)

    with ZipFile('sources-{}.zip'.format(file.filename), 'w') as zip:
        zip.write('separated/demucs_extra/{}/bass.wav'.format(file.filename.replace('.mp3', '')),
                  basename('separated/demucs_extra/{}/bass.wav'.format(file.filename.replace('.mp3', ''))))
        zip.write('separated/demucs_extra/{}/drums.wav'.format(file.filename.replace('.mp3', '')),
                  basename('separated/demucs_extra/{}/drums.wav'.format(file.filename.replace('.mp3', ''))))
        zip.write('separated/demucs_extra/{}/other.wav'.format(file.filename.replace('.mp3', '')),
                  basename('separated/demucs_extra/{}/other.wav'.format(file.filename.replace('.mp3', ''))))
        zip.write('separated/demucs_extra/{}/vocals.wav'.format(file.filename.replace('.mp3', '')),
                  basename('separated/demucs_extra/{}/vocals.wav'.format(file.filename.replace('.mp3', ''))))

    background_tasks.add_task(cleanup, file.filename, name)

    return FileResponse('sources-{}.zip'.format(file.filename), media_type='application/zip', filename='sources-{}.zip'.format(name))


@app.get("/")
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
