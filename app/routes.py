import os
import json
import tempfile
from io import BytesIO
from flask import (Blueprint, render_template, request, redirect, send_file,
                   flash, current_app)
from werkzeug.utils import secure_filename

from .constants import ALLOWED_EXTENSIONS, GET, POST
from .table_processor import TableProcessor

main_bp = Blueprint('main', __name__)


def allowed_file(filename):
    """
    Determine if a filename has an allowed extension.

    Args:
        filename (str): Name of the uploaded file.

    Returns:
        bool: True if the file extension is in ALLOWED_EXTENSIONS,
              False otherwise.
    """
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/', methods=[GET, POST])
def upload_and_process():
    """
    Handle GET and POST requests to upload and process a .docx file.

    On GET: render the upload form.
    On POST: validate and save the uploaded file, process it with
    table_processor, and return a JSON download.

    Returns:
        flask.Response: A redirect, a rendered template,
        or a file download response.
    """
    if request.method == POST:

        file = request.files.get('file')
        if not file or file.filename == '' or not allowed_file(file.filename):
            flash('Please, upload a valid .docx file')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_dir = (
                current_app.config.get('UPLOAD_FOLDER') or tempfile.gettempdir())
        filepath = os.path.join(upload_dir, filename)
        os.makedirs(upload_dir, exist_ok=True)
        file.save(filepath)

        table_obj = TableProcessor(file_path=filepath)
        results = table_obj.process_tables()

        buf = BytesIO(
            json.dumps(results, ensure_ascii=False, indent=2).encode('utf-8'))
        buf.seek(0)
        download_name = f"{os.path.splitext(filename)[0]}_processed.json"

        return send_file(
            buf,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/json'
        )

    return render_template('upload.html')
