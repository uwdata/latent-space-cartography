import Store from '../controllers/store'
import Vue from 'vue'

const DTYPE = {
  numeric: 'numeric',
  categorical: 'categorical'
}

const config_default = {
  dataset: 'emoji',
  data_type: 'image',
  train_split: 13500,
  initial_dim: 32,
  initial_projection: 't-SNE',
  schema: {
    'type': {},
    'meta': ['i','name', 'mean_color', 'category', 'platform', 'version', 'codepoints', 'shortcode']
  },
  rendering: {
    dot_color: 'mean_color',
    ext: 'png',
  },
  search: {
    advanced: true,
    by: ['name', 'codepoints', 'shortcode'],
    filter: 'platform'
  },
  filter: null,
  color_by: null,
  y_axis: null
}

/**
 * Toggle dataset here!
 */
let CONFIG = config_default

const DEBUG = process.env.NODE_ENV === 'development'

/**
 * Only outputs if we are in dev build.
 */
function log_debug (...args) {
  if (DEBUG) {
    console.log(...args)
  }
}

function setConfig (config) {
  CONFIG = config
}

/**
 * Shared store.
 */
let store = new Store()

/**
 * Global event bus.
 */
let bus = new Vue()

export {
  DEBUG,
  CONFIG,
  DTYPE,
  store,
  bus,
  log_debug,
  setConfig
}

