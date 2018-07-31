#!flask/bin/python
import json
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
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
# from config_emoji import dset, data_type, img_rows, img_cols, img_chns, img_mode, dims, schema_meta
from config_tybalt import dset, data_type, dims, schema_meta

# FIXME: hack
temp_store = {}

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

# instantiate the model from our image generation VAE
def create_model (latent_dim):
    base = './data/{}/models/{}/'.format(dset, latent_dim)
    mpath = abs_path(base + '{}_model_dim={}.json'.format(dset, latent_dim))
    wpath = abs_path(base + '{}_model_dim={}.h5'.format(dset, latent_dim))
    m = model.Vae(latent_dim = latent_dim, img_dim=(img_chns, img_rows, img_cols))
    models[latent_dim] = m.read(mpath, wpath) + (m,)

# instantiate the model that's simply an h5py file
def load_model (latent_dim):
    from keras.models import load_model

    mpath = './data/{}/models/{}_model_dim={}.h5'.format(dset, dset, latent_dim)
    decoder = load_model(mpath)
    models[latent_dim] = decoder

# read latent space
def read_ls (latent_dim):
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

# given a list of points in latent space, generate their corresponding images
def _generate_image (latent_dim, points):
    if not latent_dim in models:
        create_model(latent_dim)
    vae, encoder, decoder, m = models[latent_dim]

    print('Predicting ...')
    images = []
    for idx, val in enumerate(points):
        val = val.reshape((1, latent_dim))
        recon = m.to_image(decoder.predict(val))
        img = Image.fromarray(recon, img_mode)
        images.append(img)
    print('Done.')

    return images

# given a list of points in latent space, reconstruct via decoder
# the reconstruction results are just arbitrary tensors
def _generate_other (latent_dim, points):
    if not latent_dim in models:
        load_model(latent_dim)
    decoder = models[latent_dim]
    points = np.asarray(points, float)
    return decoder.predict(points)

# number of points within L2 distance of a given point
# also return the nearest neighbor
def _num_neighbors (X, points, distance = 3.0):
    count = []
    nearest = []
    n, latent_dim = X.shape
    for idx, p in enumerate(points):
        P = np.repeat(p.reshape(1, -1), n, axis = 0)
        # d = np.abs(X - P)
        d = np.linalg.norm(X - P, axis = 1) # L2 distance
        qualify = np.less_equal(d, np.repeat(distance, n))
        indices = np.where(qualify)[0]
        count.append(len(indices))
        nearest.append(np.argmin(d))
    return count, nearest

# sample points along a vector
def _sample_vec (start, end, n_samples = 8, over = True):
    loc = []
    for i in range(n_samples + 1):
        k = float(i) / n_samples
        loc.append((1-k) * start + k * end)

    # overshoot
    if over:
        k = 1.5
        loc.append((1-k) * start + k * end)
    return loc

# interpolate between two points in a latent space
# return a list of reconstructed outputs sampled at equal steps along the path
def _interpolate (X, start, end):
    n, latent_dim = X.shape
    if data_type == 'image':
        loc = _sample_vec(start, end)
        # generate these images
        recon = _generate_image(latent_dim, loc)
    else:
        loc = _sample_vec(start, end, 1, False)
        # generate tensor outputs
        recon = _generate_other(latent_dim, loc)
    count, nn = _num_neighbors(X, loc)

    return loc, recon, count, nn

# linear orthogonal transformation of all points to the given axis
def _project_axis (X, axis):
    n, latent_dim = X.shape

    # 1. make the axis a unit vector
    axis = np.asarray(axis, dtype=np.float64)
    v = preprocessing.normalize(axis.reshape(1, -1))

    # v is a row vector of shape (1, latent_dim)
    if v.shape[1] != latent_dim:
        print 'Could not project to axis because axis and latent dimension shape mismatch.'
        return jsonify({'status': 'fail'}), 200

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

    # compute the variation of v
    # FIXME: the variance doesn't seem correct
    print 'Explained variance: {}'.format(pca.explained_variance_)
    total_var = pca.explained_variance_.sum()
    print 'Total variance: {}'.format(total_var)
    s = np.dot(X, v.T)
    s = np.sum(s ** 2) / (n - 1)
    print 'Variance of x axis: {}, {}%'.format(s, s / total_var)

    return X_transformed, U, mean_

# given a group ID, query the DB for image indices, as an int array
def _get_group_indices (gid):
    # find image indices in each group
    cursor.execute('SELECT list FROM {}_group WHERE id={}'.format(dset, gid))
    d = cursor.fetchone()[0]
    id_list = d.split(',')

    # compute centroid
    indices = np.asarray(id_list, dtype=np.int16)
    return indices

# compute the centroid of a group
def _compute_group_centroid (X, gid):
    indices = _get_group_indices(gid)
    centroid = np.sum(X[indices], axis=0) / indices.shape[0]

    return centroid

# compute the average inter-point distance (L2) between each point pair
def _pointwise_dist (X, Y=None):
    R = X if Y is None else Y
    m, _ = X.shape
    n, _ = R.shape

    s = 0
    for i in range(m):
        # left hand matrix: repeat an element N times
        L = np.repeat([X[i]], n, axis=0)
        D = np.linalg.norm(L - R, axis=1)
        # for intra-cluster distance, exclude self
        denom = n - 1 if Y is None else n
        s += np.sum(D) / float(denom)
    
    return s / float(m)

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
    img =  _generate_image(latent_dim, re[i:i+1])[0]
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
    query = 'SELECT {} FROM {}_meta'.format(schema_meta, dset)
    cursor.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

# apply analogy
@app.route('/api/apply_analogy', methods=['POST'])
def apply_analogy ():
    latent_dim = request.json['latent_dim']
    pid = request.json['pid']
    gid = request.json['groups'].split(',')

    # FIXME
    if not 'U' in temp_store or temp_store['U'].shape[1] != latent_dim:
        print 'Could not apply anaology because projection is corrupt.'
        print temp_store['U'].shape
        return jsonify({}), 400
    U = temp_store['U']
    _mean = temp_store['_mean']

    # read latent space
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])

    # compute centroid
    vec = _compute_group_centroid(X, gid[1]) - _compute_group_centroid(X, gid[0])

    start = X[int(pid)]
    end = start + vec

    loc, images, count, nearest = _interpolate(X, start, end)
    fns = []
    for idx, img in enumerate(images):
        img_fn = 'analogy_{}_{}.png'.format(pid, idx)
        fns.append(img_fn)
        img.save(abs_path('./build/' + img_fn))

    # project to visualize path
    loc = np.dot(loc - _mean, U.T)

    reply = {
        'outputs': fns,
        'locations': loc.tolist(),
        'neighbors': count,
        'nearest': nearest
    }

    return jsonify(reply), 200

# bring a vector to focus: interpolate along the path, and reproject all points
@app.route('/api/focus_vector', methods=['POST'])
def focus_vector():
    latent_dim = request.json['latent_dim']
    gid = request.json['groups'].split(',')
    reply = {}

    # read latent space
    X = read_ls(latent_dim)
    
    # compute centroid
    start = _compute_group_centroid(X, gid[0])
    end = _compute_group_centroid(X, gid[1])
    vec = end - start

    # project
    X_transformed, U, _mean = _project_axis(np.copy(X), vec)
    temp_store['U'] = U #FIXME
    temp_store['_mean'] = _mean
    reply['points'] = X_transformed.tolist()

    # interpolate
    if data_type == 'image':
        loc, images, count, nearest = _interpolate(X, start, end)
        loc = np.dot(loc - _mean, U.T)
        recon = []
        for idx, img in enumerate(images):
            img_fn = '{}_{}.png'.format('to'.join(gid), idx)
            recon.append(img_fn)
            img.save(abs_path('./build/' + img_fn))
    elif data_type == 'other':
        loc, recon, count, nearest = _interpolate(X, start, end)
        loc = np.dot(loc - _mean, U.T)
        recon = recon.tolist()

    if recon is not None:
        reply['outputs'] = recon
        reply['locations'] = loc.tolist()
        reply['neighbors'] = count
        reply['nearest'] = nearest

    return jsonify(reply), 200

@app.route('/api/all_vector_diff', methods=['POST'])
def all_vector_diff ():
    # get all attribute vectors from database
    query = 'SELECT a.start, a.end FROM {}_vector a'.format(dset)
    cursor.execute(query)
    data = [list(i) for i in cursor.fetchall()]

    # compute vector coordinates in each latent space
    vecs = {}
    for dim in dims:
        X = read_ls(dim)
        arr = []
        for v in data:
            arr.append(_compute_group_centroid(X, v[1]) - _compute_group_centroid(X, v[0]))
        vecs[dim] = np.asarray(arr)

    # compute cosine similarity between each possible vector pair
    cos = {}
    for dim in dims:
        vs = vecs[dim]
        arr = []
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                arr.append(cosine_similarity(vs[i].reshape(1, -1), vs[j].reshape(1, -1))[0][0])
        cos[dim] = np.asarray(arr)

    # compare each adjacent latent dim
    for i in range(len(dims) - 1):
        L = cos[dims[i]]
        R = cos[dims[i + 1]]
        diff = np.sum(np.abs(R - L)) / float(L.shape[0])
        print '{} and {}: {}'.format(dims[i], dims[i + 1], diff)

    return jsonify({'status': 'success'}), 200

# compute a number to represent how focused an attribute vector is
@app.route('/api/vector_score', methods=['POST'])
def vector_score ():
    latent_dim = request.json['latent_dim']
    gid = request.json['groups'].split(',')

    # read latent space
    X = read_ls(latent_dim)
    
    # data points in start and end group
    start = X[_get_group_indices(gid[0])]
    end = X[_get_group_indices(gid[1])]
    n, _ = start.shape
    m, _ = end.shape

    # all possible vector pairs between start and end
    L = np.repeat(start, m, axis=0)
    R = np.tile(end, (n, 1))
    V = L - R

    # cosine similarity
    cs = cosine_similarity(V)
    score = np.mean(cs)
    print 'Vector score (GID {} & {}): average {}, min {}'.format(gid[0], \
        gid[1], round(score, 2), round(np.amin(cs), 2))

    return jsonify({'score': score}), 200

# compute a number to represent how tight a cluster is
@app.route('/api/cluster_score', methods=['POST'])
def cluster_score ():
    latent_dim = request.json['latent_dim']
    ids = request.json['ids']

    X = read_ls(latent_dim)
    a = _pointwise_dist(X[ids])
    b = _pointwise_dist(X[ids], np.delete(X, ids, axis=0))
    print 'Intra-cluster distance: {}, Inter-cluster distance: {}'.format(a, b)
    # this score resembles silhouette score, but it replaces inter-cluster
    # distance with the average length of all edges with one node inside and one outside.
    score = (b - a) / max(a, b)

    return jsonify({'score': score}), 200

# save a group
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

# get all groups
@app.route('/api/get_groups', methods=['POST'])
def get_groups ():
    query = 'SELECT id, alias, list, timestamp FROM {}_group'.format(dset)
    cursor.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data}), 200

# delete a group
@app.route('/api/delete_group', methods=['POST'])
def delete_group ():
    gid = request.json['id']
    query = 'DELETE FROM {}_group WHERE id={}'.format(dset, gid)
    print query

    cursor.execute(query)
    db.commit()
    return jsonify({'status': 'success'}), 200

# create a vector
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

# get all vectors
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

# delete a vector
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
