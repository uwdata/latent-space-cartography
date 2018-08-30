import http from 'axios'
import _ from 'lodash'
import {DATASET, CONFIG, log_debug} from './config'

const nPC = 4

/**
 * Handles client-server connection and serves as a central data store for client.
 * Also contains data manipulation functions.
 */
class Store {
  constructor () {
    /**
     * Dictionary to save PCA points, key by latent dimension
     */
    this.pca = {}

    /**
     * Dictionary to save t-SNE points, key by latent dimension and perplexity
     */
    this.tsne = {}

    /**
     * Image meta data, including index, company name, average color, and more.
     */
    this.meta = []

    /**
     * Meta data about what each input dimension means
     */
    this.header = []

    /**
     * An array of indices of user's favorite points.
     * Warning: do not re-assign the pointer! Only mutate the content of the array.
     */
    this.selected = []

    /**
     * Groups of logos.
     */
    this.groups = []

    /**
     * Matrix and mean for attribute vector projection.
     * @private
     */
    this._projection_matrix = null
    this._projection_mean = null

    // FIXME: latent dim shouldn't be here
    this.latent_dim = 32

    /**
     * Display help information in prominent places.
     */
    this.tutorial = {
      vector: false
    }

    /**
     * Coordination between UI components
     */
    this.state = {
      tab: 0, // 0 - group, 1 - vector
      detail: null,
      detail_card: null,
      clicked_point: null
    }
  }

  /**
   * Async get the image meta data from server.
   * @returns {Promise}
   */
  getMeta () {
    return new Promise((resolve, reject) => {
      // we already have the meta data locally
      if (this.meta.length) {
        resolve(this.meta)
        return
      }

      // data schema
      let schema = CONFIG.schema.meta
      let schema_header = CONFIG.schema.header

      // go fetch from the server
      http.post('/api/get_meta', {})
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.meta = _.map(msg.meta, (m) => {
              let result = {}
              _.each(m, (val, idx) => {
                result[schema[idx]] = val
              })
              return result
            })

            this.header = !msg.header ? [] : _.map(msg.header, (m) => {
              let result = {}
              _.each(m, (val, idx) => {
                result[schema_header[idx]] = val
              })
              return result
            })
            resolve()
          } else {
            reject(`Fail to initialize.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   * Async get the points after PCA from server
   * @param dim The latent dimension (since models differ only in latent dim)
   * @param pca_dim The number of principal components in PCA
   * @returns {Promise}
   */
  getPcaPoints (dim, pca_dim = nPC) {
    this.latent_dim = dim
    return new Promise((resolve, reject) => {
      if (this.pca[dim]) {
        resolve(this.pca[dim].points)
        return
      }

      let payload = {'latent_dim': dim, 'pca_dim': pca_dim, 'indices': []}

      this.getMeta()
        .then(() => {
          return http.post('/api/get_pca', payload)
        })
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.pca[dim] = {
              points: this._formatPcaPoints(msg.data, []),
              variation: msg.variation
            }
            resolve(this.pca[dim].points)
          } else {
            reject(`Fail to initialize.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   *
   * @param dim
   * @param subset If non-empty, perform PCA on just these points
   */
  customPca (dim, subset = []) {
    return new Promise((resolve, reject) => {
      let payload = {'latent_dim': dim, 'pca_dim': 2, 'indices': subset}

      http.post('/api/get_pca', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            let points = this._formatPcaPoints(msg.data, subset)
            resolve(points)
          } else {
            reject(`Fail to initialize.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   * Synchronous version of retrieving PCA points.
   * @param dim
   * @returns Array
   */
  getPcaPointsSync (dim) {
    if (this.pca[dim]) {
      return this.pca[dim].points
    }
    return []
  }

  /**
   * Synchronous version of retrieving PCA explained variances.
   * @param dim
   * @returns Array
   */
  getPcaVarSync (dim) {
    if (this.pca[dim]) {
      return this.pca[dim].variation
    }
    return []
  }

  /**
   * Async get the t-SNE result from server
   * @param dim
   * @param perp t-SNE perplexity parameter.
   * @param pca
   */
  getTsnePoints (dim, perp, pca = false) {
    let key = this.tsneKey(dim, perp, pca)
    return new Promise((resolve, reject) => {
      if (this.tsne[key]) {
        resolve(this.tsne[key])
        return
      }

      let payload = {'latent_dim': dim, 'perplexity': perp, 'pca': pca}

      this.getMeta()
        .then(() => {
          return http.post('/api/get_tsne', payload)
        })
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.tsne[key] = this._formatPoints(msg.data)
            resolve(this.tsne[key])
          } else {
            reject(`Fail to initialize.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   * Get the dictionary key for a particular t-SNE result.
   * Then you can retrieve the result in this.tsne[key]
   * @param dim
   * @param perp
   * @param pca
   * @returns {string}
   */
  tsneKey (dim, perp, pca = false) {
    return `${dim}_${perp}_${pca ? 'pca' : ''}`
  }

  /**
   * Get the raw (input) data for the i-th sample
   * Useful when input data type is arbitrary vector
   * @param i
   */
  getRaw (i) {
    return new Promise((resolve, reject) => {
      http.post('/api/get_raw', {'i': i})
        .then((response) => {
          let msg = response.data

          if (msg) {
            resolve(_.map(msg.data, (val, idx) => {
              return _.assign({}, this.header[idx], {'i': idx, 'value': val})
            }))
          } else {
            reject(`Internal server error.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   * Given a point in the PCA space, transform it back to latent space and then to images.
   * @param x
   * @param y
   * @param i The index.
   * @returns {Promise}
   */
  transformPoint (x, y, i) {
    return new Promise((resolve, reject) => {
      let payload = {'latent_dim': this.latent_dim, 'x': x, 'y': y, 'i': i}

      http.post('/api/pca_back', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            resolve(msg.image)
          } else {
            reject(`Fail to initialize.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   * Save a list of logo id to the server.
   * @param ids A list of logo id.
   * @param alias Optional alias to identify this save.
   */
  saveLogoList (ids, alias = '') {
    return new Promise((resolve, reject) => {
      let payload = {'alias': alias, ids: ids.join(',')}

      http.post('/api/save_group', payload)
        .then((response) => {
          let msg = response.data

          if (msg && msg['status'] === 'success') {
            resolve()
          } else {
            reject(`Could not save to the database.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Get all logo lists
   */
  getLogoLists () {
    return new Promise((resolve, reject) => {
      http.post('/api/get_groups', {})
        .then((response) => {
          let msg = response['data']

          let schema = ['id', 'alias', 'list', 'timestamp']

          if (msg) {
            this.groups = _.map(msg['data'], (arr) => {
              let result = {}
              _.each(arr, (val, idx) => {
                result[schema[idx]] = val
              })
              result.list = _.map(result.list.split(','), (i) => Number(i))
              return result
            })
            resolve()
          } else {
            reject(`Could not get the list.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Delete a logo group by its group id.
   * @param id
   * @returns {Promise}
   */
  deleteLogoList (id) {
    return new Promise((resolve, reject) => {
      let payload = {id: id}

      http.post('/api/delete_group', payload)
        .then((response) => {
          let msg = response.data

          if (msg && msg['status'] === 'success') {
            resolve()
          } else {
            reject(`Could not delete from database.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Save a vector to database.
   * @param start
   * @param end
   * @param description
   * @returns {Promise}
   */
  createVector (start, end, description = '') {
    return new Promise((resolve, reject) => {
      let payload = {'start': start, 'end': end, 'desc': description}

      http.post('/api/create_vector', payload)
        .then((response) => {
          let msg = response.data

          if (msg && msg['status'] === 'success') {
            resolve()
          } else {
            reject(`Could not save to the database.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Get all vectors.
   * @returns {Promise}
   */
  getVectors () {
    return new Promise((resolve, reject) => {
      let payload = {}

      http.post('/api/get_vectors', payload)
        .then((response) => {
          let msg = response.data

          let schema = ['id', 'description', 'timestamp', 'start', 'end',
            'list_start', 'list_end', 'alias_start', 'alias_end']

          if (msg) {
            let vectors = _.map(msg['data'], (arr) => {
              let result = {}
              _.each(arr, (val, idx) => {
                result[schema[idx]] = val
              })
              result.list_start = _.map(result.list_start.split(','), (i) => Number(i))
              result.list_end = _.map(result.list_end.split(','), (i) => Number(i))
              return result
            })

            resolve(vectors)
          } else {
            reject(`Could not read from database.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  deleteVector (vid) {
    return new Promise((resolve, reject) => {
      let payload = {'id': vid}

      http.post('/api/delete_vector', payload)
        .then((response) => {
          let msg = response.data

          if (msg && msg['status'] === 'success') {
            resolve()
          } else {
            reject(`Could not delete from the database.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Get the coordinate of vectors to visualize in a global projection.
   * @param latent_dim
   * @param {string} projection - Projection code that encodes multiple info
   * @param {array} vectors - A 2D array of start and end group id per vector
   * @returns {Promise}
   */
  plotVectors (latent_dim, projection, vectors) {
    // parse projection string
    let perp = ''
    if (/^tsne/.test(projection)) {
      perp = projection.split('-')[1]
      projection = 'tsne'
    }

    let matrix = ''
    let mean = ''
    if (projection === 'vector') {
      matrix = this._projection_matrix
      mean = this._projection_mean
    }

    // serialize vectors
    vectors = _.map(vectors, (v) => v.join(',')).join(';')

    return new Promise((resolve, reject) => {
      let payload = {latent_dim: latent_dim, projection: projection,
        perplexity: perp, pca_dim: nPC, matrix: matrix, mean: mean,
        vectors: vectors}

      http.post('/api/plot_vectors', payload)
        .then((response) => {
          let msg = response['data']

          if (msg && msg.status === 'success') {
            // data is a 2D array, in the same sequence as input vectors
            // for t-SNE, each vector gets an array of control points
            // for PCA, each vector gets an array of the first several PCs
            resolve(_.map(msg.data, (path) => _.map(path, (pt) => {
              let res = {x: pt[0], y: pt[1]}
              if (/pca/i.test(projection)) {
                _.each(pt, (val, j) => {
                  res[`PC${j + 1}`] = val
                })
              }
              return res
            })))
          } else {
            reject(msg ? msg.message : 'Oops ... server error.')
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Bring a vector to focus.
   * @param latent_dim
   * @param start Group id of the starting group.
   * @param end Group id of the ending group.
   * @returns {Promise}
   */
  focusVector (latent_dim, start, end) {
    return new Promise((resolve, reject) => {
      let payload = {groups: [start, end].join(','), latent_dim: latent_dim}

      http.post('/api/focus_vector', payload)
        .then((response) => {
          let msg = response['data']

          if (msg) {
            this._projection_matrix = msg['projection']
            this._projection_mean = msg['mean']

            let points = this._formatPcaPoints(msg['points'])
            let line = this._formatVectorLine(msg['locations'], msg['neighbors'],
              msg['outputs'], msg['nearest'])
            let top = CONFIG.data_type === 'other' ? [this._joinHeader(msg['top_start']),
              this._joinHeader(msg['top_end'])] : []
            resolve([points, line, top])
          } else {
            reject()
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Pairwise cosine similarity between a vector and all other vectors.
   * @param latent_dim
   * @param {number} vid - The id of the vector.
   * @returns {Promise}
   */
  vectorDiff (latent_dim, vid) {
    return new Promise((resolve, reject) => {
      let payload = {vid: vid, latent_dim: latent_dim}

      http.post('/api/vector_diff', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            resolve(msg['data'])
          } else {
            reject(`Internal server error.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Apply the analogy vector
   * @param latent_dim
   * @param pid Number Point index of the data point to apply analogy to.
   * @param start Number Group ID of the starting group.
   * @param end Number Group ID of the ending group.
   */
  applyAnalogy (latent_dim, pid, start, end) {
    return new Promise((resolve, reject) => {
      let payload = {pid: pid, latent_dim: latent_dim, groups: `${start},${end}`,
        projection: this._projection_matrix, mean: this._projection_mean}

      http.post('/api/apply_analogy', payload)
        .then((response) => {
          let msg = response['data']

          if (msg) {
            let line = this._formatVectorLine(msg['locations'], msg['neighbors'],
              msg['outputs'], msg['nearest'])
            let answer = CONFIG.data_type === 'text' ?
              this._formatKnn(msg['knn_indices'], msg['knn_distances']) : []
            resolve([line, answer])
          } else {
            reject()
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  vectorScore (latent_dim, start, end) {
    return new Promise((resolve, reject) => {
      let payload = {groups: [start, end].join(','), latent_dim: latent_dim}

      http.post('/api/vector_score', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            resolve(msg['score'])
          } else {
            reject(`Internal server error.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  clusterScore (latent_dim, ids) {
    return new Promise((resolve, reject) => {
      if (ids.length < 2) {
        return resolve(0)
      }

      let payload = {'latent_dim': latent_dim, ids: ids}

      http.post('/api/cluster_score', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            resolve(msg['score'])
          } else {
            reject(`Internal server error.`)
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Given the index, return a relative URL to the image.
   * @param i
   * @returns {string}
   */
  getImageUrl (i) {
    return `/data/${DATASET}/images/${i}.${CONFIG.rendering.ext}`
  }

  /**
   * Add one or more point indices to the selected array.
   * @param is Array An array of indices to be added.
   */
  addToSelected (is) {
    let dict = _.zipObject(this.selected, _.map(this.selected, () => true))
    _.each(_.uniq(is), (i) => {
      if (!dict[i]) {
        this.selected.push(i)
      }
    })
  }

  /**
   * Perform a join between given points array and meta, with key 'i'
   * @param points
   * @private
   */
  _joinMeta (points) {
    let meta_dict = _.keyBy(this.meta, 'i')
    return _.map(points, (p) => _.assign(p, meta_dict[p.i]))
  }

  /**
   * Map input dimension index to corresponding header
   * @param vec
   * @private
   */
  _joinHeader (vec) {
    vec = vec || []
    if (!this.header || !this.header.length) {
      log_debug('[WARNING]: lack input header information.')
      return vec
    }
    let meta_dict = _.keyBy(this.header, 'i')
    return _.map(vec, (v) => _.assign(v, meta_dict[v.i]))
  }

  _formatKnn (idx, dist) {
    return _.range(idx.length).map((j) => {
      return { i: idx[j], name: this.meta[idx[j]].name, distance: dist[j] }
    })
  }

  _formatVectorLine (locations, neighbors, outputs, nearest) {
    outputs = outputs || []
    let n = neighbors.length
    return _.range(n).map((j) => {
      let res = {
        x: locations[j][0],
        y: locations[j][1],
        neighbors: neighbors[j],
        output: outputs[j],
        nearest: nearest[j]
      }
      if (CONFIG.data_type === 'image') {
        res.image = res.output
      }
      return res
    })
  }

  _formatPcaPoints (points, indices = []) {
    // points is a 2D array with shape: (length, n_components)
    return this._joinMeta(_.map(points, (p, i) => {
      // p is a 1D array containing n_components float
      let res = {i: indices.length ? indices[i] : i}

      _.forEach(p, (pp, j) => {
        let key = `PC${j + 1}`
        res[key] = Number(Number(pp).toFixed(3))
      })

      // backward compatibility
      res['x'] = res['PC1']
      res['y'] = res['PC2']
      return res
    }))
  }

  _formatPoints (data) {
    return this._joinMeta(_.map(data, (d, idx) => {
      return {
        'x': Number(d[0]),
        'y': Number(d[1]),
        'i': idx
      }
    }))
  }
}

export default Store
