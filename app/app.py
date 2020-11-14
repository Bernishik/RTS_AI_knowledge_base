from flask import Flask, render_template, request
from config import Config
from db import add_triplets_to_db, get_query_item, shortest_way_label

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


# REST methon add triplets in graph
@app.route('/add_triplets', methods=["POST"])
def add_triplets():
    if request.method == "POST":
        data = request.get_json(force=True)
        add_triplets_to_db(data)
        return render_template('index.html')


@app.route('/get_item', methods=["POST"])
def get_item():
    data = request.get_json(force=True)
    result = get_query_item(data)
    return result


@app.route('/shortest_way', methods=["POST"])
def shortest_way():
    data = request.get_json(force=True)
    label_1, label_2 = None, None
    if "label_1" in data:
        label_1 = data['label_1']
    if "label_2" in data:
        label_2 = data['label_2']

    result = shortest_way_label(data, label_1=label_1, label_2=label_2)
    return result


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
