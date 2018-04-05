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
from flaskext.mysql import MySQL

# re-use keras models
models = {}

# for absolute path
def abs_path (rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)

def connect_db ():
    # read config file
    with open(abs_path('mysql_config.json')) as jsonfile:
        app.config.update(json.load(jsonfile))
    
    mysql = MySQL()
    mysql.init_app(app)
    conn = mysql.connect()
    cursor =conn.cursor()
    print 'MySQL connected!'

    return cursor

# global app and DB cursor
app = Flask(__name__, static_url_path='')
cursor = connect_db()

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
@app.route('/api/get_pca', methods=['POST'])
def get_pca ():
    if not request.json or not 'latent_dim' in request.json:
        abort(400)
    
    latent_dim = request.json['latent_dim']
    pca_dim = int(request.json['pca_dim'])
    indices = np.asarray(request.json['indices'], dtype=np.int16)

    rawpath = abs_path('./data/latent/latent{}.h5'.format(latent_dim))
    with h5py.File(rawpath, 'r') as f:
        raw = np.asarray(f['latent'])
        length = indices.shape[0]
        if length > 0:
            raw = raw[indices]

        pca = PCA(n_components = pca_dim)
        d = pca.fit_transform(raw)
        va = pca.explained_variance_ratio_

    print 'Explained variation per principal component: {}'.format(va)

    return jsonify({'data': d.tolist(), 'variation': va.tolist()}), 200

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
    rawpath = abs_path('./data/latent/latent{}.h5'.format(latent_dim))
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
        mpath = abs_path(base + 'logo_model_dim={}.json'.format(latent_dim))
        wpath = abs_path(base + 'logo_model_dim={}.h5'.format(latent_dim))
        m = model.Vae(latent_dim = latent_dim)
        models[latent_dim] = m.read(mpath, wpath) + (m,)

    vae, encoder, decoder, m = models[latent_dim]
    print('predicting ...')
    recon = m.to_image(decoder.predict(re[i:i+1]))

    img = Image.fromarray(recon, 'RGB')
    img_fn = '{}.png'.format(int(time.time()))
    img.save(abs_path('./build/' + img_fn))

    return jsonify({'latent': re[i].tolist(), 'image': img_fn}), 200

# get tsne data
@app.route('/api/get_tsne', methods=['POST'])
def get_tsne ():
    if not request.json or not 'latent_dim' in request.json:
        abort(400)
    
    latent_dim = request.json['latent_dim']
    perp = request.json['perplexity']
    suffix = '_pca' if request.json['pca'] else ''
    fn = abs_path('./data/tsne/tsne{}_perp{}{}.json'.format(latent_dim, perp, suffix))
    print(fn)
    with open(fn) as data_file:
        data = json.load(data_file)
    
    return jsonify({'data': data}), 200

# get meta data
@app.route('/api/get_meta', methods=['POST'])
def get_meta ():
    cursor.execute('SELECT i,name,mean_color,data_source,industry FROM meta')
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

if __name__ == '__main__':
    app.run(debug=True) # change to (host= '0.0.0.0') in production
