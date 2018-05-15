import http from 'axios'
import _ from 'lodash'
import {DATASET, IMG_EXT, SCHEMAS} from './config'

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
     * An array of indices of user's favorite points.
     * Warning: do not re-assign the pointer! Only mutate the content of the array.
     */
    this.selected = []

    /**
     * Groups of logos.
     */
    this.groups = []

    // FIXME: latent dim shouldn't be here
    this.latent_dim = 32

    /**
     * Coordination between UI components
     */
    this.tab = {
      index: 0 // 0 - group, 1 - vector
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
      let schema = SCHEMAS[DATASET].meta

      // go fetch from the server
      http.post('/api/get_meta', {})
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.meta = _.map(msg.data, (m) => {
              let result = {}
              _.each(m, (val, idx) => {
                result[schema[idx]] = val
              })
              return result
            })
            resolve(this.meta)
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
  getPcaPoints (dim, pca_dim = 2) {
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

  /**
   * Interpolate between the centroid of two groups
   * @param groups Array of database ID of the first group
   * @param latent_dim
   */
  interpolateBetween (groups, latent_dim) {
    return new Promise((resolve, reject) => {
      let payload = {groups: groups.join(','), latent_dim: latent_dim}
      console.log(payload)

      http.post('/api/interpolate_group', payload)
        .then((response) => {
          let msg = response['data']

          if (msg) {
            console.log(msg)
            resolve([msg['anchors'], msg['vec'], msg['neighbors']])
          } else {
            reject()
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  /**
   * Apply the analogy vector
   * @param latent_dim
   * @param pid
   * @param vec The analogy vector.
   */
  applyAnalogy (latent_dim, pid, vec) {
    return new Promise((resolve, reject) => {
      let payload = {pid: pid, latent_dim: latent_dim, vec: vec}
      console.log(payload)

      http.post('/api/apply_analogy', payload)
        .then((response) => {
          let msg = response['data']

          if (msg) {
            resolve([msg['anchors'], msg['neighbors']])
          } else {
            reject()
          }
        }, () => {
          reject(`Could not connect to the server.`)
        })
    })
  }

  projectToAxis (latent_dim, axis) {
    return new Promise((resolve, reject) => {
      let payload = {latent_dim: latent_dim, axis: axis}
      console.log(payload)

      http.post('/api/project_axis', payload)
        .then((response) => {
          let msg = response['data']

          if (msg) {
            let points = this._formatPcaPoints(msg['data'])
            resolve(points)
          } else {
            reject()
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
    return `/data/${DATASET}/images/${i}.${IMG_EXT}`
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

  _formatPcaPoints (points, indices = []) {
    // points is a 2D array with shape: (length, n_components)
    return this._joinMeta(_.map(points, (p, i) => {
      // p is a 1D array containing n_components float
      let res = {i: indices.length ? indices[i] : i}

      _.forEach(p, (pp, j) => {
        let key = `PC${j}`
        res[key] = Number(Number(pp).toFixed(3))
      })

      // backward compatibility
      res['x'] = res['PC0']
      res['y'] = res['PC1']
      return res
    }))
  }

  _formatPoints (points) {
    return this._joinMeta(_.map(points, (p) => {
      return {
        'x': Number(p.x),
        'y': Number(p.y),
        'i': p.i
      }
    }))
  }
}

export default Store
