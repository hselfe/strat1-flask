# This file is UNUSED - just keeping it for testing
from flask import Flask, render_template, request, flash
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
import pandas as pd
from forms import ContactForm

from bson import json_util
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
# Connect to organisations
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["MONGO_URI"] = "mongodb+srv://hselfe:pymongo2112@cluster0-ru7km.mongodb.net/test?retryWrites=true&w=majority/"
pymongo = PyMongo(app)

app.secret_key = 'development_key'

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            return 'Form posted.'
    elif request.method == 'GET':
        return render_template('contact.html', form=form)

@socketio.on('connect')
def handleConnection():
    print('connection established')

@socketio.on('listen_for_changes')
def listen_for_changes(data):
    print(data)
    with pymongo.cx['DeepTrade_v1'].stratOne.watch() as stream:
        for change in stream:
            print(json.dumps(change, default=json_util.default))
            socketio.emit('update_data', json.dumps(change, default=json_util.default))

@app.route('/')
def index():
    collection_demo = pymongo.cx['DeepTrade_v1'].symbols
    cursor_demo = collection_demo.find().sort("_id")
    df = pd.DataFrame(list(cursor_demo))
    return render_template('strat_one.html', df_strat1 = df)

if __name__ == '__main__':
    socketio.run(app)