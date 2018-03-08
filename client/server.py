#!flask/bin/python
import json
from sklearn.decomposition import PCA
import numpy as np
import h5py
import sys
import os
import time
from PIL import Image

# ugly way to import a file from another directory ...
sys.path.append(os.path.join(os.path.dirname(__file__), '../model'))
import model

from flask import Flask, send_from_directory, send_file
from flask import request, jsonify

# re-use keras models
models = {}

# global app
app = Flask(__name__, static_url_path='')

# static files
@app.route('/')
def index ():
    return send_file('index.html')

# static files
@app.route('/build/<path:path>')
def serve_public (path):
    return send_from_directory('build', path)
@app.route('/data/<path:path>')
def serve_data (path):
    return send_from_directory('data', path)

# get pca data
# TODO: pca is fast, we don't really need those intermediate files ...
# TODO: fix all the relative paths
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
    
    # project from 2D to latent space
    rawpath = './data/latent/latent{}.h5'.format(latent_dim)
    with h5py.File(rawpath, 'r') as f:
        raw = f['latent']
        pca = PCA(n_components=2)
        pca.fit(raw)

        d = pca.transform(raw)
        d[i] = [x, y]

        re = pca.inverse_transform(d)

    # project from latent space to image
    if not latent_dim in models:
        base = './data/models/{}/'.format(latent_dim)
        mpath = base + 'logo_model_dim={}.json'.format(latent_dim)
        wpath = base + 'logo_model_dim={}.h5'.format(latent_dim)
        m = model.Vae(latent_dim = latent_dim)
        models[latent_dim] = m.read(mpath, wpath) + (m,)

    vae, encoder, decoder, m = models[latent_dim]
    print('predicting ...')
    recon = m.to_image(decoder.predict(re[i:i+1]))

    img = Image.fromarray(recon, 'RGB')
    img_fn = '{}.png'.format(int(time.time()))
    img.save('./build/' + img_fn)

    return jsonify({'latent': re[i].tolist(), 'image': img_fn}), 200

if __name__ == '__main__':
    app.run(debug=True)
