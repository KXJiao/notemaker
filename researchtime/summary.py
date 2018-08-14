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
import magic
# ConRanker imports
from . import ConRanker


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx', 'html', 'htm', 'epub', 'jpg', 'jpeg', 'png'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def summarize(text, num):
#     parser = PlaintextParser.from_string(text, Tokenizer('english'))
#     summarizer = LexRankSummarizer()
#     summary = summarizer(parser.document, num)
#     summarized = []
#     for sentence in summary:
#         summarized.append(str(sentence))
#     return summarized



bp = Blueprint('summary', __name__)
@bp.route('/', methods=['GET', 'POST'])
def index():
    processed = ''
    filecontent = ''
    if request.method == 'POST':
        sentenceNum = 5
        try:
            snum = int(request.form['sentNum'])
            if snum >0 and snum < 100:
                sentenceNum = snum
        except:
            sentenceNum = 5

        #Summarize textbox
        if 'compare' in request.form:
            raw_text = request.form['text']
            if raw_text != '':
                filecontent = raw_text
                processed = ConRanker.summary(raw_text, sentenceNum)#summarize(raw_text, sentenceNum)
                return render_template('summary/processed.html', processed=processed, filecontent=filecontent)
            return ''

        #Summarize uploaded file
        elif 'upload' in request.form:
            if 'file' not in request.files:
                return 'No file'
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
                tobeprocessed = textract.process(url_for('summary.uploaded_file', filename=filename))
                processed = ConRanker.summary(tobeprocessed, sentenceNum)#summarize(tobeprocessed, sentenceNum)

                os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

                return render_template('summary/processed.html', processed=processed, filecontent=tobeprocessed)
            return 'File not allowed'

        #Summarize file from URL
        elif 'external' in request.form:
            #add code to check if proper url
            link = request.form['url']
            if link == '' or not validators.url(link):
                return 'Bad URL'
            r = requests.get(link, allow_redirects=True)
            filename = link.rsplit('/', 1)[1]
            print('downloading: ' + filename)
            if r and allowed_file(filename):
                ext = filename.rsplit('.', 1)[1].lower()
                filename = str(uuid.uuid4()) + '.' + ext 
                basedir = os.path.abspath(os.path.dirname(__file__))
                with app.open_instance_resource(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                    f.write(r.content)

                unprocessed = textract.process(url_for('summary.uploaded_file', filename=filename))
                processed = ConRanker.summary(unprocessed, sentenceNum)#summarize(unprocessed, sentenceNum)

                os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

                return render_template('summary/processed.html', processed=processed, filecontent=unprocessed)
            return 'File not allowed'



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
        senNumNum = 5

    if sm_type == 'text':
        text = data.get('data')
        if text != '':
            # send the highlighted text as well
            processed = ConRanker.summary(text, senNum)#summarize(text, senNum)
            summarized = []
            for sentence in processed:
                summarized.append(str(sentence))


            return jsonify(og=text,summary=summarized)#highlight='blahblah'
        return jsonify(og='',summary='')#highlight=''

    elif sm_type == 'url':

        #############################################################################3
            link = data.get('data')
            if link == '' or not validators.url(link):
                return 'Bad URL'
            r = requests.get(link, allow_redirects=True)
            filename = link.rsplit('/', 1)[1]
            print('downloading: ' + filename)
            if r and allowed_file(filename):
                ext = filename.rsplit('.', 1)[1].lower()
                filename = str(uuid.uuid4()) + '.' + ext 
                basedir = os.path.abspath(os.path.dirname(__file__))
                with app.open_instance_resource(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                    f.write(r.content)

                unprocessed = textract.process(url_for('summary.uploaded_file', filename=filename))
                processed = ConRanker.summary(unprocessed, sentenceNum)#summarize(unprocessed, sentenceNum)

                os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

                return render_template('summary/processed.html', processed=processed, filecontent=unprocessed)
            return 'File not allowed'
        #############################################################################3
        unprocessed = textract.process(url_for('summary.uploaded_file', filename=uploadfilename))
        processed = ConRanker.summary(unprocessed, senNum)
        summarized = []
        for sentence in processed:
            summarized.append(str(sentence))

        return jsonify(og=unprocessed,summary=summarized)


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


            processed = ConRanker.summary(tobeprocessed, sentenceNum)#summarize(tobeprocessed, sentenceNum)

            os.remove(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

            return jsonify(og=tobeprocessed,summary=processed)
        print('File not allowed')
        return 'File not allowed'



@bp.route('/tmp/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
