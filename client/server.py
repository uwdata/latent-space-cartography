#!flask/bin/python
import json
from sklearn.decomposition import PCA
import numpy as np
import h5py

from flask import Flask, send_from_directory, send_file
from flask import request, jsonify

app = Flask(__name__, static_url_path='')

# static files
@app.route('/')
def index ():
    return send_file('index.html')

# static files
@app.route('/build/<path:path>')
def serve_public (path):
    return send_from_directory('build', path)

# get pca data
# TODO: pca is fast, we don't really need those intermediate files ...
@app.route('/api/get_pca', methods=['POST'])
def get_pca ():
    if not request.json or not 'latent_dim' in request.json:
        abort(400)
    
    latent_dim = request.json['latent_dim']
    fn = './data/pca/pca{}.json'.format(latent_dim)
    with open(fn) as data_file:
        data = json.load(data_file)
    
    return jsonify({'data': data}), 200

# PCA backward projection
@app.route('/api/pca_back', methods=['POST'])
def pca_back ():
    if not request.json:
        abort(400)
    
    latent_dim = request.json['latent_dim']
    x = float(request.json['x'])
    y = float(request.json['y'])
    i = int(request.json['i'])
    
    rawpath = './data/latent/latent{}.h5'.format(latent_dim)
    with h5py.File(rawpath, 'r') as f:
        raw = f['latent']
        pca = PCA(n_components=2)
        pca.fit(raw)

        d = pca.transform(raw)
        d[i] = [x, y]

        re = pca.inverse_transform(d)

    return jsonify({'data': re[i].tolist()}), 200

if __name__ == '__main__':
    app.run(debug=True)
