import http from 'axios'
import _ from 'lodash'

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

    // FIXME: latent dim shouldn't be here
    this.latent_dim = 32
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

      let payload = {'latent_dim': dim, 'pca_dim': pca_dim}

      http.post('/api/get_pca', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.pca[dim] = {
              points: this._formatPcaPoints(msg.data),
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

      http.post('/api/get_tsne', payload)
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

  _formatPcaPoints (points) {
    // points is a 2D array with shape: (length, n_components)
    return _.map(points, (p, i) => {
      // p is a 1D array containing n_components float
      let res = {i: i}

      _.forEach(p, (pp, j) => {
        let key = `PC${j}`
        res[key] = Number(Number(pp).toFixed(3))
      })

      // backward compatibility
      res['x'] = res['PC0']
      res['y'] = res['PC1']
      return res
    })
  }

  _formatPoints (points) {
    return _.map(points, (p) => {
      return {
        'x': Number(p.x),
        'y': Number(p.y),
        'i': p.i
      }
    })
  }
}

export default Store
