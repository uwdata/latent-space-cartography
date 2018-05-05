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

# dataset we're working with
dset = 'logo'

# FIXME: store in DB
last_vec = {}

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

    return conn, cursor

def create_model (latent_dim):
    base = './data/{}/models/{}/'.format(dset, latent_dim)
    mpath = abs_path(base + '{}_model_dim={}.json'.format(dset, latent_dim))
    wpath = abs_path(base + '{}_model_dim={}.h5'.format(dset, latent_dim))
    m = model.Vae(latent_dim = latent_dim)
    models[latent_dim] = m.read(mpath, wpath) + (m,)

# global app and DB cursor
app = Flask(__name__, static_url_path='')
db, cursor = connect_db()

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

    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
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
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        raw = f['latent']
        pca = PCA(n_components=2)
        pca.fit(raw)

        d = pca.transform(raw)
        d[i] = [x, y]

        re = pca.inverse_transform(d)

    # project from latent space to image
    if not latent_dim in models:
        create_model(latent_dim)

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
    fn = abs_path('./data/{}/tsne/tsne{}_perp{}{}.json'.format(dset, latent_dim, perp, suffix))
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

# apply analogy
@app.route('/api/apply_analogy', methods=['POST'])
def apply_analogy ():
    latent_dim = request.json['latent_dim']
    pid = request.json['pid']

    vec = last_vec['temp'] if 'temp' in last_vec else np.zeros(1)

    if latent_dim != vec.shape[0]:
        print 'Could not apply analogy because last vector is shape {}'.format(last_vec.shape)
        return jsonify({}), 400

    # read latent space
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        raw = np.asarray(f['latent'])
    start = raw[int(pid)]
    end = start + vec

    print(vec)

    # sample the points along the vector
    # TODO: now only works for two groups
    n_samples = 7
    loc = []
    for i in range(n_samples + 1):
        k = float(i) / n_samples
        loc.append((1-k) * start + k * end)
    # overshoot
    k = 2
    loc.append((1-k) * start + k * end)

    # generate these images
    if not latent_dim in models:
        create_model(latent_dim)
    vae, encoder, decoder, m = models[latent_dim]

    print('predicting ...')
    fns = []
    for idx, val in enumerate(loc):
        val = val.reshape((1, latent_dim))
        recon = m.to_image(decoder.predict(val))
        img = Image.fromarray(recon, 'RGB')
        img_fn = 'analogy_{}_{}.png'.format(pid, idx)
        fns.append(img_fn)
        img.save(abs_path('./build/' + img_fn))

    return jsonify({'anchors': fns}), 200


# interpolate between the centroids of two groups
@app.route('/api/interpolate_group', methods=['POST'])
def interpolate_group ():
    latent_dim = request.json['latent_dim']
    gid = request.json['groups'].split(',')

    # read latent space
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        raw = np.asarray(f['latent'])
    
    # find image indices in each group
    ids = []
    for g in gid:
        cursor.execute('SELECT list FROM logo_list WHERE id={}'.format(g))
        d = cursor.fetchone()[0]
        ids.append(d.split(','))
    
    # compute centroid
    centroids = []
    for id_list in ids:
        indices = np.asarray(id_list, dtype=np.int16)
        centroid = np.sum(raw[indices], axis=0) / indices.shape[0]
        centroids.append(centroid)

    #FIXME
    last_vec['temp'] = centroids[1] - centroids[0]

    # sample the points along the vector
    # TODO: now only works for two groups
    n_samples = 7
    loc = []
    for i in range(n_samples + 1):
        k = float(i) / n_samples
        loc.append((1-k) * centroids[0] + k * centroids[1])
    # overshoot
    k = 2
    loc.append((1-k) * centroids[0] + k * centroids[1])

    # generate these images
    if not latent_dim in models:
        create_model(latent_dim)
    vae, encoder, decoder, m = models[latent_dim]

    print('predicting ...')
    fns = []
    for idx, val in enumerate(loc):
        val = val.reshape((1, latent_dim))
        recon = m.to_image(decoder.predict(val))
        img = Image.fromarray(recon, 'RGB')
        img_fn = '{}_{}.png'.format('to'.join(gid), idx)
        fns.append(img_fn)
        img.save(abs_path('./build/' + img_fn))

    return jsonify({'anchors': fns}), 200
    # return jsonify({'latent': re[i].tolist(), 'image': img_fn}), 200

# save logo list
@app.route('/api/save_logo_list', methods=['POST'])
def save_logo_list ():
    if not request.json or not 'ids' in request.json:
        abort(400)

    ids = request.json['ids']
    alias = request.json['alias'] if 'alias' in request.json else ''

    query = """
    INSERT INTO logo_list (alias, list)
    VALUES('{}', '{}')
    """.format(alias, ids)
    print query

    try:
        cursor.execute(query)
        db.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print("Could not insert: \n" + str(e))
        return jsonify({'status': 'fail'}), 200

@app.route('/api/get_logo_lists', methods=['POST'])
def get_logo_lists ():
    cursor.execute('SELECT id, alias, list, timestamp FROM logo_list')
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

# create logo list table. internal use only
@app.route('/api/_create_logo_list', methods=['POST'])
def _create_logo_list ():
    query = """
    CREATE TABLE `logo_list` (
        `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
        `alias` varchar(255) DEFAULT NULL,
        `list` TEXT,
        `creation_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `timestamp` TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """
    cursor.execute(query)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True) # change to (host= '0.0.0.0') in production
