#!flask/bin/python
import json
from sklearn.decomposition import PCA
from sklearn import preprocessing
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

# given a list of points in latent space, generate their corresponding images
def _generate (latent_dim, points):
    if not latent_dim in models:
        create_model(latent_dim)
    vae, encoder, decoder, m = models[latent_dim]

    print('Predicting ...')
    images = []
    for idx, val in enumerate(points):
        val = val.reshape((1, latent_dim))
        recon = m.to_image(decoder.predict(val))
        img = Image.fromarray(recon, 'RGB')
        images.append(img)
    print('Done.')

    return images

# number of points within L2 distance of a given point
def _num_neighbors (X, points, distance = 3.0):
    res = []
    n, latent_dim = X.shape
    for idx, p in enumerate(points):
        P = np.repeat(p.reshape(1, -1), n, axis = 0)
        # d = np.abs(X - P)
        d = np.linalg.norm(X - P, axis = 1) # L2 distance
        qualify = np.less_equal(d, np.repeat(distance, n))
        indices = np.where(qualify)[0]
        res.append(len(indices))
    return res

# interpolate between two points in a latent space
# return a list of images sampled at equal steps along the path
def _interpolate (X, start, end):
    n, latent_dim = X.shape

    # sample the points along the vector
    n_samples = 7
    loc = []
    for i in range(n_samples + 1):
        k = float(i) / n_samples
        loc.append((1-k) * start + k * end)
    # overshoot
    k = 2
    loc.append((1-k) * start + k * end)

    # generate these images
    return _generate(latent_dim, loc), _num_neighbors(X, loc)

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
    img =  _generate(latent_dim, re[i:i+1])[0]
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
    if dset == 'logo':
        query = 'SELECT i,name,mean_color,data_source,industry FROM logo_meta'
    elif dset == 'emoji':
        query = 'SELECT i, mean_color FROM emoji_meta'
    cursor.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

# apply analogy
@app.route('/api/apply_analogy', methods=['POST'])
def apply_analogy ():
    latent_dim = request.json['latent_dim']
    pid = request.json['pid']
    vec = np.asarray(request.json['vec'], dtype=np.float64)

    if latent_dim != vec.shape[0]:
        print 'Could not apply analogy because last vector is shape {}'.format(vec.shape)
        return jsonify({}), 400

    # read latent space
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        raw = np.asarray(f['latent'])
    start = raw[int(pid)]
    end = start + vec

    images, count = _interpolate(raw, start, end)
    fns = []
    for idx, img in enumerate(images):
        img_fn = 'analogy_{}_{}.png'.format(pid, idx)
        fns.append(img_fn)
        img.save(abs_path('./build/' + img_fn))

    return jsonify({'anchors': fns, 'neighbors': count}), 200


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
        cursor.execute('SELECT list FROM {}_group WHERE id={}'.format(dset, g))
        d = cursor.fetchone()[0]
        ids.append(d.split(','))
    
    # compute centroid
    centroids = []
    for id_list in ids:
        indices = np.asarray(id_list, dtype=np.int16)
        centroid = np.sum(raw[indices], axis=0) / indices.shape[0]
        centroids.append(centroid)

    vec = centroids[1] - centroids[0]

    images, count = _interpolate(raw, centroids[0], centroids[1])
    fns = []
    for idx, img in enumerate(images):
        img_fn = '{}_{}.png'.format('to'.join(gid), idx)
        fns.append(img_fn)
        img.save(abs_path('./build/' + img_fn))

    return jsonify({'anchors': fns, 'vec': vec.tolist(), 'neighbors': count}), 200

# linear orthogonal transformation of all points to the given axis
@app.route('/api/project_axis', methods=['POST'])
def project_axis ():
    latent_dim = request.json['latent_dim']
    axis = request.json['axis']

    # 1. make the axis a unit vector
    axis = np.asarray(axis, dtype=np.float64)
    v = preprocessing.normalize(axis.reshape(1, -1))

    # v is a row vector of shape (1, latent_dim)
    if v.shape[1] != latent_dim:
        print 'Could not project to axis because axis and latent dimension shape mismatch.'
        return jsonify({'status': 'fail'}), 200

    # read latent space
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])

    # 2. center X to mean
    mean_ = np.mean(X, axis=0)
    X -= mean_

    # 3. substract the first axis from X (project X to the d-1 orthogonal space of axis)
    X_hat = X - np.dot(X, np.dot(v.T, v))

    # 4. perform PCA
    pca = PCA(n_components = 2)
    pca.fit(X_hat)
    y = pca.components_[0]
    va = pca.explained_variance_ratio_

    print 'Explained variance ratio: {}'.format(va)

    U = np.append(v, y.reshape(1, -1), axis=0)
    X_transformed = np.dot(X, U.T)

    #TODO: compuate side views for x and y axes

    # compute the variation of v
    # FIXME: the variance doesn't seem correct
    print 'Explained variance: {}'.format(pca.explained_variance_)
    total_var = pca.explained_variance_.sum()
    print 'Total variance: {}'.format(total_var)
    n_samples = X.shape[0]
    s = np.dot(X, v.T)
    s = np.sum(s ** 2) / (n_samples - 1)
    print 'Variance of x axis: {}, {}%'.format(s, s / total_var)

    return jsonify({'data': X_transformed.tolist()}), 200

# save logo list
@app.route('/api/save_group', methods=['POST'])
def save_group ():
    if not request.json or not 'ids' in request.json:
        abort(400)

    ids = request.json['ids']
    alias = request.json['alias'] if 'alias' in request.json else ''

    query = """
    INSERT INTO {}_group (alias, list)
    VALUES('{}', '{}')
    """.format(dset, alias, ids)
    print query

    try:
        cursor.execute(query)
        db.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print("Could not insert: \n" + str(e))
        return jsonify({'status': 'fail'}), 200

@app.route('/api/get_groups', methods=['POST'])
def get_groups ():
    query = 'SELECT id, alias, list, timestamp FROM {}_group'.format(dset)
    cursor.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

@app.route('/api/create_vector', methods=['POST'])
def create_vector():
    start = request.json['start']
    end = request.json['end']
    desc = request.json['desc']

    query = """INSERT INTO {}_vector (start, end, description)
    VALUES('{}', '{}', '{}')""".format(dset, start, end, desc)
    print query

    try:
        cursor.execute(query)
        db.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print("Could not insert: \n" + str(e))
        return jsonify({'status': 'fail'}), 200

@app.route('/api/get_vectors', methods=['POST'])
def get_vectors ():
    query = """
    SELECT a.id, a.description, a.timestamp, a.start, a.end, b.list AS list_start,
      c.list AS list_end, b.alias AS alias_start, c.alias AS alias_end
    FROM {}_vector a
    LEFT OUTER JOIN (SELECT id, list, alias FROM {}_group) AS b ON a.start = b.id
    LEFT OUTER JOIN (SELECT id, list, alias FROM {}_group) AS c ON a.end = c.id
    """.format(dset, dset, dset)
    cursor.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

@app.route('/api/delete_vector', methods=['POST'])
def delete_vector ():
    vid = request.json['id']

    query = 'DELETE FROM {}_vector WHERE id={}'.format(dset, vid)
    print query

    try:
        cursor.execute(query)
        db.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print("Could not delete: \n" + str(e))
        return jsonify({'status': 'fail'}), 200

# create the groups table. internal use only
@app.route('/api/_create_table_group', methods=['POST'])
def _create_table_group ():
    query = """
    CREATE TABLE `{}_group` (
        `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
        `alias` varchar(255) DEFAULT NULL,
        `list` TEXT,
        `creation_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `timestamp` TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """.format(dset)
    cursor.execute(query)
    return jsonify({'status': 'success'}), 200

# create the vectors table. internal use only
@app.route('/api/_create_table_vector', methods=['POST'])
def _create_table_vector ():
    query = """
    CREATE TABLE `{}_vector` (
        `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
        `description` varchar(255) DEFAULT NULL,
        `start` int(11),
        `end` int(11),
        `creation_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `timestamp` TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
    """.format(dset)
    cursor.execute(query)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True) # change to (host= '0.0.0.0') in production
