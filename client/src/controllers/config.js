import Store from '../controllers/store'

const DEBUG = process.env.NODE_ENV === 'development'

/**
 * Only outputs if we are in dev build.
 */
function log_debug (...args) {
  if (DEBUG) {
    console.log(...args)
  }
}

/**
 * Shared store.
 */
let store = new Store()

export {
  DEBUG,
  store,
  log_debug
}

