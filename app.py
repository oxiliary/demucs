import os
import shutil
import subprocess
from zipfile import ZipFile

from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()


def cleanup(file, name):
    """Remove files generated from request."""
    os.remove('sources-{}.zip'.format(name))
    os.remove('ready/{}'.format(file))
    shutil.rmtree('separated')


def get_source_paths(directory):
    """Gather bass, vocals, drums, and other."""
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


@app.post("/uploadfiles/")
async def create_upload_files(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """"Entrypoint for source separation."""
    upload_folder = open(os.path.join('ready/', file.filename), 'wb+')
    shutil.copyfileobj(file.file, upload_folder)
    upload_folder.close()
    subprocess.call(
        ['python -m demucs.separate {}/ready/{} --dl -n demucs_extra -d cpu'.format(os.getcwd(), file.filename)], shell=True)

    name = file.filename.replace('.mp3', '')

    source_paths = get_source_paths('separated/demucs_extra/{}'.format(name))

    with ZipFile('sources-{}.zip'.format(name), 'w') as zip:
        for source in source_paths:
            zip.write(source)

    background_tasks.add_task(cleanup, file.filename, name)

    return FileResponse('sources-{}.zip'.format(name), media_type='application/zip', filename='sources-{}.zip'.format(name))


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
