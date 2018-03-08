const DEBUG = process.env.NODE_ENV === 'development'

/**
 * Only outputs if we are in dev build.
 */
function log_debug (...args) {
  if (DEBUG) {
    console.log(...args)
  }
}

export {
  DEBUG,
  log_debug
}

