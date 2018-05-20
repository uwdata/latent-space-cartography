import Store from '../controllers/store'

const config_logo = {
  dataset: 'logo',
  train_split: 15000,
  ext: 'jpg'
}

const config_emoji = {
  dataset: 'emoji',
  train_split: 13500,
  ext: 'png'
}

/**
 * Toggle dataset here!
 */
let c = config_emoji

const DEBUG = process.env.NODE_ENV === 'development'
const DATASET = c.dataset
const TRAIN_SPLIT = c.train_split
const IMG_EXT = c.ext

/**
 * Database schemas, keyed by dataset name first, then table name.
 */
let SCHEMAS = {}

SCHEMAS[config_logo.dataset] = {
  'meta': ['i', 'name', 'mean_color', 'source', 'industry']
}
SCHEMAS[config_emoji.dataset] = {
  'meta': ['i','name', 'mean_color', 'category', 'platform', 'version', 'codepoints', 'shortcode']
}

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
  TRAIN_SPLIT,
  IMG_EXT,
  DATASET,
  SCHEMAS,
  store,
  log_debug
}

