from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory, jsonify
)
from flask import current_app as app
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os
from os.path import abspath
import requests
import uuid
import textract
import validators
import sys
from PIL import Image
import pytesseract
import mimetypes
# ConRanker imports
from . import ConRanker

'''
                'image/png': 
                'image/jpeg': 
                'image/pjpeg':
                'application/pdf':
                'application/msword':
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                'text/plain':
                'text/html':
                'application/epub+zip':
'''
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx', 'html', 'htm', 'epub', 'jpg', 'jpeg', 'png'])
ALLOWED_MIME = set(['text/plain', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/html', 'image/jpeg', 'image/pjpeg', 'image/png'])
MIME_TO_EXT = {
    'text/plain':'txt', 
    'application/pdf':'pdf', 
    'application/msword':'doc', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':'docx', 
    'text/html':'html', 
    'image/jpeg':'jpg', 
    'image/pjpeg':'jpg', 
    'image/png':'png'   
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_mime(mimetype):
    return '/' in mimetype and mimetype.lower() in ALLOWED_MIME


bp = Blueprint('summary', __name__)
@bp.route('/', methods=['GET', 'POST'])
def index():
    processed = ''
    filecontent = ''

    return render_template('summary/index.html', processed=processed, filecontent=filecontent)

@bp.route('/textsummary')
def textsummary():
    return render_template('summary/processed.html')



@bp.route('/summarize', methods=['GET', 'POST'])
def smmze():
    data = request.get_json()
    print(data, file=sys.stderr)
    print(request.data, file=sys.stderr)
    sm_type = data.get('type')
    senNum = 5
    try:
        snum = int(data.get('num'))
        print(snum, file=sys.stderr)
        if snum >0 and snum < 50:
            senNum = snum
    except:
        senNum = 5

    if sm_type == 'text':
        text = data.get('data')
        if text != '':
            # send the highlighted text as well
            subject = ConRanker.getSubject(text)
            processed = ConRanker.summary(text, senNum)#summarize(text, senNum)
            summarized = []
            for sentence in processed:
                summarized.append(str(sentence))


            return jsonify(og=text,summary=summarized,subject=subject)#highlight='blahblah'
        return jsonify(og='',summary='',subject='')#highlight=''

    elif sm_type == 'url':

        #############################################################################3
        link = data.get('data')
        errors = 'nothing here for now but will be changed in due time. when me president, they see'
        if link == '' or not validators.url(link):
            return 'Bad URL'
        r = requests.get(link, allow_redirects=True)
        print(r.status_code)
        if r.status_code == 200:
            conttype = r.headers['content-type'].split(';', 1)[0]
            print("ur content type is: ",conttype)
            filename = link.rsplit('/', 1)[1]
            print('downloading: ' + filename)

            if r and allowed_mime(conttype):
                ext = MIME_TO_EXT.get(conttype)#filename.rsplit('.', 1)[1].lower()
                filename = str(uuid.uuid4()) + '.' + ext 
                basedir = os.path.abspath(os.path.dirname(__file__))
                with app.open_instance_resource(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                    f.write(r.content)

                unprocessed = ''
                if not (ext == 'jpg' or ext == 'jpeg' or ext == 'png' or ext == 'gif'):
                    unprocessed = textract.process(url_for('summary.uploaded_file', filename=filename))
                else:
                    img = Image.open(url_for('summary.uploaded_file', filename=filename))
                    unprocessed = pytesseract.image_to_string(img, lang='eng')

                try:
                    unprocessed = unprocessed.decode('utf-8')
                except AttributeError:
                    pass
                subject = ConRanker.getSubject(unprocessed)
                processed = ConRanker.summary(unprocessed, senNum)#summarize(unprocessed, sentenceNum)

                os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

                summarized = []

                for sentence in processed:
                    summarized.append(str(sentence))

                return jsonify(og=unprocessed,summary=summarized,subject=subject)
            return jsonify(error=errors)
        #############################################################################3

    return 'test'

#summarizer for file uploads
@bp.route('/fileupload', methods=['GET', 'POST'])
def filesmmze():
    if request.method == 'POST':

        sentenceNum = 5
        try:
            snum = int(request.form['sentNum'])
            if snum >0 and snum < 100:
                sentenceNum = snum
        except:
            sentenceNum = 5

        if 'file' not in request.files:
                print('no file')
                return jsonify(error='nofile')
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            file.filename = str(uuid.uuid4()) + '.' + ext
            filename = secure_filename(file.filename)
            print('uploading: ' + filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
            tobeprocessed = ''
            if not (ext == 'jpg' or ext == 'jpeg' or ext == 'png' or ext == 'gif'):
                tobeprocessed = textract.process(url_for('summary.uploaded_file', filename=filename))
            else:
                img = Image.open(url_for('summary.uploaded_file', filename=filename))
                tobeprocessed = pytesseract.image_to_string(img, lang='eng')
            try:
                tobeprocessed = tobeprocessed.decode('utf-8')
            except AttributeError:
                pass

            subject = ConRanker.getSubject(tobeprocessed)
            processed = ConRanker.summary(tobeprocessed, sentenceNum)#summarize(tobeprocessed, sentenceNum)

            os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

            summarized = []
            for sentence in processed:
                summarized.append(str(sentence))

            return jsonify(og=tobeprocessed,summary=processed,subject=subject)
        print('File not allowed')
        return 'File not allowed'



@bp.route('/tmp/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
