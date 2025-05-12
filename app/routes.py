import os
import json
import tempfile
from flask import (Blueprint, render_template, request, redirect, url_for, send_file,
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

        # Save results to a JSON file for later download
        download_name = f"{os.path.splitext(filename)[0]}_processed.json"
        json_path = os.path.join(upload_dir, download_name)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        # Redirect to thank-you page, passing the filename and original filename
        return redirect(
            url_for("main.thank_you",
                    filename=download_name,
                    original_filename=filename)
        )

    return render_template('upload.html')


@main_bp.route('/download/<filename>')
def download_file(filename):
    """
    Serve the processed JSON file for download.
    """
    upload_dir = current_app.config.get('UPLOAD_FOLDER') or tempfile.gettempdir()
    file_path = os.path.join(upload_dir, filename)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )


@main_bp.route('/thank_you/<filename>')
def thank_you(filename):
    """
    Render a thank-you page after successful file processing.

    Args:
        filename (str): The name of the processed JSON file.

    Returns:
        Flask Response: The rendered thank-you template.
    """
    original_filename = request.args.get('original_filename', filename)
    return render_template(
        'thank_you.html',
        filename=filename,
        original_filename=original_filename)
