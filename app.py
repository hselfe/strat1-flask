from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
import pandas as pd

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

@socketio.on('connect')
def handleConnection():
    print('connection established')

@socketio.on('listen_for_changes')
def listen_for_changes(data):
    print(data)
    with pymongo.cx['DeepTrade_v1'].stratOne.watch() as stream:
        for change in stream:
            print(json.dumps(change, default=json_util.default))
            # this_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            # print(this_time)
            #new_data = [nd.to_json() for nd in change['fullDocument']]
            socketio.emit('update_data', json.dumps(change, default=json_util.default)) #change['fullDocument']['Symbol'])  #, latest_time = this_time)

@app.route('/')
def index():
    collection_demo = pymongo.cx['DeepTrade_v1'].symbols
    cursor_demo = collection_demo.find().sort("_id")
    df = pd.DataFrame(list(cursor_demo))
    return render_template('strat_one.html', df_strat1 = df)

if __name__ == '__main__':
    socketio.run(app)