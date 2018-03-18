import http from 'axios'
import _ from 'lodash'

/**
 * Handles client-server connection and serves as a central data store for client.
 * Also contains data manipulation functions.
 */
class Store {
  constructor () {
    this.pca = {}
    // FIXME: latent dim shouldn't be here
    this.latent_dim = 32
    this.tsne = {}
  }

  /**
   * Async get the points after PCA from server
   * @param dim The latent dimension (since models differ only in latent dim)
   * @returns {Promise}
   */
  getPcaPoints (dim) {
    this.latent_dim = dim
    return new Promise((resolve, reject) => {
      if (this.pca[dim]) {
        resolve(this.pca[dim])
        return
      }

      let payload = {'latent_dim': dim}

      http.post('/api/get_pca', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.pca[dim] = this._formatPoints(msg.data)
            resolve(this.pca[dim])
          } else {
            reject(`Fail to initialize.`)
          }
        }, () => {
          reject(`Network error.`)
        })
    })
  }

  /**
   * Async get the t-SNE result from server
   * @param dim
   */
  getTsnePoints (dim) {
    this.latent_dim = dim
    return new Promise((resolve, reject) => {
      if (this.tsne[dim]) {
        resolve(this.tsne[dim])
        return
      }

      let payload = {'latent_dim': dim}

      http.post('/api/get_tsne', payload)
        .then((response) => {
          let msg = response.data

          if (msg) {
            this.tsne[dim] = this._formatPoints(msg.data)
            resolve(this.tsne[dim])
          } else {
            reject(`Fail to initialize.`)
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
