#!flask/bin/python
import json
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import KDTree
from sklearn import preprocessing
from scipy.stats import norm
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
# from config_emoji import img_rows, img_cols, img_chns, img_mode
from config_glove_6b import dset, data_type, dims, schema_meta, schema_header, metric

# for absolute path
def abs_path (rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)

# wrapper class for database
class DB:
    conn = None

    def __init__(self):
        # read config file
        with open(abs_path('mysql_config.json')) as jsonfile:
            app.config.update(json.load(jsonfile))
        
        self.mysql = MySQL()
        self.mysql.init_app(app)

    def execute(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
        except: #TODO: handle specific error
            self.conn = self.mysql.connect()
            print 'MySQL connected!'
            cursor = self.conn.cursor()
            cursor.execute(query)
        return cursor, self.conn
    
    def safe_commit(self, conn, cursor):
        try:
            conn.commit()
        except:
            conn.rollback()
        finally:
            cursor.close()

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

def read_raw ():
    p_raw = abs_path('./data/{}/raw.h5'.format(dset))
    with h5py.File(p_raw, 'r') as f:
        X = np.asarray(f['data'])
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

# given a vector w, return the index in top and bottom quantile
# the quantile is computed as highsd away in a standard normal distribution
def _top_and_bottom (w, highsd=2.5):
    n = w.shape[0]
    cutoff = n - int(n * norm.cdf(highsd))
    srt = np.argsort(w)
    w = w.tolist() # numpy float32 is not JSON serializable
    pos = [{'i': i, 'diff': w[i]} for i in srt[-cutoff:]]
    neg = [{'i': i, 'diff': w[i]} for i in srt[:cutoff]]
    return pos[::-1], neg

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
    elif data_type == 'other':
        loc = _sample_vec(start, end, 1, False)
        # generate tensor outputs
        recon = _generate_other(latent_dim, loc)
    else:
        loc = _sample_vec(start, end, 1, False)
        recon = None
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
    cursor, conn = db.execute('SELECT list FROM {}_group WHERE id={}'.format(dset, gid))
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

# compute k nearest neighbors using cosine distance
def _knn_cosine (X, v, kn = 20):
    tree = KDTree(preprocessing.normalize(X))
    _, idx = tree.query(v, k=kn)
    dist = cosine_similarity(X[idx[0]], np.repeat(v, kn, axis=0))
    return dist[:, 0], idx[0]

# global app and DB cursor
app = Flask(__name__, static_url_path='')
db = DB()

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
    fn = abs_path('./data/{}/tsne/tsne{}_perp{}{}.h5'.format(dset, latent_dim, perp, suffix))
    with h5py.File(fn, 'r') as f:
        data = np.asarray(f['tsne']) # shape: (n, 2)
    print(fn)

    return jsonify({'data': data.tolist()}), 200

# get meta data
@app.route('/api/get_meta', methods=['POST'])
def get_meta ():
    query = 'SELECT {} FROM {}_meta'.format(schema_meta, dset)
    cursor, conn = db.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    reply = {'meta': data}

    # header is meta data on input data columns
    if schema_header:
        query = 'SELECT {} FROM {}_header'.format(schema_header, dset)
        cursor.execute(query)
        header = [list(i) for i in cursor.fetchall()]
        reply['header'] = header

    return jsonify(reply), 200

# apply analogy
@app.route('/api/apply_analogy', methods=['POST'])
def apply_analogy ():
    latent_dim = request.json['latent_dim']
    pid = request.json['pid']
    gid = request.json['groups'].split(',')

    U = np.asarray(request.json['projection'], dtype=np.float64)
    _mean = np.asarray(request.json['mean'], dtype=np.float64)

    # read latent space
    rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])

    # compute centroid
    vec = _compute_group_centroid(X, gid[1]) - _compute_group_centroid(X, gid[0])

    start = X[int(pid)]
    end = start + vec

    if data_type == 'image':
        loc, images, count, nearest = _interpolate(X, start, end)
        fns = []
        for idx, img in enumerate(images):
            img_fn = 'analogy_{}_{}.png'.format(pid, idx)
            fns.append(img_fn)
            img.save(abs_path('./build/' + img_fn))
        
        reply = { 'outputs': fns }
    else:
        loc, _, count, nearest = _interpolate(X, start, end)
        dist, idx = _knn_cosine(X, end.reshape(1, -1))
        reply = { 'knn_indices': idx.tolist(), 'knn_distances': dist.tolist() }

    loc = np.dot(loc - _mean, U.T)
    reply['locations'] = loc.tolist()
    reply['neighbors'] = count
    reply['nearest'] = nearest

    return jsonify(reply), 200

# visualize vectors together in a global projection
@app.route('/api/plot_vectors', methods=['POST'])
def plot_vectors ():
    latent_dim = request.json['latent_dim']
    projection = request.json['projection']
    vectors = request.json['vectors'].split(';')

    # read latent space
    X = read_ls(latent_dim)

    # t-SNE: use the coordinate of nearest neighbors
    if projection == 'tsne':
        # use kd-tree to compute k nearest neighbors
        tree = KDTree(X)

        # read t-SNE coordinates
        perp = request.json['perplexity']
        tpath = abs_path('./data/{}/tsne/tsne{}_perp{}.h5'.format(dset, latent_dim, perp))
        with h5py.File(tpath, 'r') as f:
            Y = np.asarray(f['tsne']) # shape: (n, 2)

        result = []
        for gids in vectors:
            # compute centroid
            gid = gids.split(',')
            start = _compute_group_centroid(X, gid[0])
            end = _compute_group_centroid(X, gid[1])
            locs = _sample_vec(start, end, over=False)

            # k nearest neighbors
            kn = 5
            dist, idx = tree.query(locs, k=kn)
            res = []
            for i in range(idx.shape[0]):
                # weighted average
                res.append(np.average(Y[idx[i]], weights=dist[i], axis=0))
            result.append(res)
        result = np.asarray(result).tolist()
        return jsonify({'status': 'success', 'data': result}), 200
    
    # PCA: multiply projection matrix directly
    elif projection == 'pca':
        pca_dim = request.json['pca_dim']
        pca = PCA(n_components = pca_dim).fit(X)
        res = []
        for gids in vectors:
            # compute centroid
            gid = gids.split(',')
            start = _compute_group_centroid(X, gid[0])
            end = _compute_group_centroid(X, gid[1])
            locs = _sample_vec(start, end, 1, False)
            res.append(np.dot(locs, pca.components_.T).tolist())
        return jsonify({'status': 'success', 'data': res}), 200
    
    # Custom vector projection: multiply custom matrix
    elif projection == 'vector':
        U = np.asarray(request.json['matrix'], dtype=np.float64)
        _mean = np.asarray(request.json['mean'], dtype=np.float64)
        res = []
        for gids in vectors:
            # compute centroid
            gid = gids.split(',')
            start = _compute_group_centroid(X, gid[0])
            end = _compute_group_centroid(X, gid[1])
            locs = _sample_vec(start, end, 1, False)
            res.append(np.dot(locs - _mean, U.T).tolist())
        return jsonify({'status': 'success', 'data': res}), 200

    return jsonify({'status': 'fail', 'message': 'unknown projection'}), 200

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
    reply['points'] = X_transformed.tolist()
    reply['mean'] = _mean.tolist()
    reply['projection'] = U.tolist()

    # interpolate
    if data_type == 'image':
        loc, images, count, nearest = _interpolate(X, start, end)
        recon = []
        for idx, img in enumerate(images):
            img_fn = '{}_{}.png'.format('to'.join(gid), idx)
            recon.append(img_fn)
            img.save(abs_path('./build/' + img_fn))
    elif data_type == 'other':
        loc, recon, count, nearest = _interpolate(X, start, end)
        # high weight genes
        diff = recon[-1] - recon[0]
        reply['top_end'], reply['top_start'] = _top_and_bottom(diff)
        recon = recon.tolist()
    else:
        loc, recon, count, nearest = _interpolate(X, start, end)

    loc = np.dot(loc - _mean, U.T)
    reply['locations'] = loc.tolist()
    reply['neighbors'] = count
    reply['nearest'] = nearest
    reply['outputs'] = recon

    return jsonify(reply), 200

@app.route('/api/vector_diff', methods=['POST'])
def vector_diff ():
    latent_dim = request.json['latent_dim']
    vid = request.json['vid']

    # get all attribute vectors from database
    query = 'SELECT a.start, a.end, a.id FROM {}_vector a'.format(dset)
    cursor, conn = db.execute(query)
    data = [list(i) for i in cursor.fetchall()]

    # compute vector coordinates
    X = read_ls(latent_dim)
    vecs = []
    idx = 0
    for i, v in enumerate(data):
        if v[2] == vid:
            idx = i
        vecs.append(_compute_group_centroid(X, v[1]) - _compute_group_centroid(X, v[0]))
    vecs = np.asarray(vecs)

    # compute cosine similarity between this vector and all others
    cos = []
    for i in range(len(vecs)):
        sim = cosine_similarity(vecs[i].reshape(1, -1), vecs[idx].reshape(1, -1))[0][0]
        cos.append({'id': data[i][2], 'cosine': sim})

    return jsonify({'data': cos}), 200

@app.route('/api/all_vector_diff', methods=['POST'])
def all_vector_diff ():
    # get all attribute vectors from database
    query = 'SELECT a.start, a.end FROM {}_vector a'.format(dset)
    cursor, conn = db.execute(query)
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

# get the k nearest neighbors of a point
@app.route('/api/get_knn', methods=['POST'])
def get_knn ():
    i = request.json['i']
    latent_dim = request.json['latent_dim']
    X = read_ls(latent_dim)
    dist, idx = _knn_cosine(X, X[i].reshape(1, -1))
    return jsonify({'knn_indices': idx.tolist(), 'knn_distances': dist.tolist()}), 200

# get the raw (input) data for a given index
# useful if the data type is arbitrary vector
@app.route('/api/get_raw', methods=['POST'])
def get_raw ():
    i = request.json['i']
    X = read_raw()
    return jsonify({'data': X[i].tolist()}), 200

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

    cursor, conn = db.execute(query)
    db.safe_commit(conn, cursor)
    return jsonify({'status': 'success'}), 200

# get all groups
@app.route('/api/get_groups', methods=['POST'])
def get_groups ():
    query = 'SELECT id, alias, list, timestamp FROM {}_group'.format(dset)
    cursor, conn = db.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data[::-1]}), 200

# delete a group
@app.route('/api/delete_group', methods=['POST'])
def delete_group ():
    gid = request.json['id']
    query = 'DELETE FROM {}_group WHERE id={}'.format(dset, gid)
    print query

    cursor, conn = db.execute(query)
    db.safe_commit(conn, cursor)
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

    cursor, conn = db.execute(query)
    db.safe_commit(conn, cursor)
    return jsonify({'status': 'success'}), 200

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
    cursor, conn = db.execute(query)
    data = [list(i) for i in cursor.fetchall()]
    return jsonify({'data': data[::-1]}), 200

# delete a vector
@app.route('/api/delete_vector', methods=['POST'])
def delete_vector ():
    vid = request.json['id']

    query = 'DELETE FROM {}_vector WHERE id={}'.format(dset, vid)
    print query

    cursor, conn = db.execute(query)
    db.safe_commit(conn, cursor)
    return jsonify({'status': 'success'}), 200

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
    db.execute(query)
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
    db.execute(query)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True) # change to (host= '0.0.0.0') in production
