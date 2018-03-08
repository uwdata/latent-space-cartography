import http from 'axios'
import _ from 'lodash'

/**
 * Handles client-server connection and serves as a central data store for client.
 * Also contains data manipulation functions.
 */
class Store {
  constructor () {
    this.pca = {}
  }

  /**
   * Async get the points after PCA from server
   * @param dim The latent dimension (since models differ only in latent dim)
   * @returns {Promise}
   */
  getPoints (dim) {
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
