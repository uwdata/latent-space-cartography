import Store from '../controllers/store'
import Vue from 'vue'

const config_logo = {
  dataset: 'logo',
  train_split: 15000,
  dims: [32, 64, 128, 256, 512, 1024],
  schema: {
    'meta': ['i', 'name', 'mean_color', 'source', 'industry']
  },
  rendering: {
    image: true,
    ext: 'jpg',
  },
  search: {
    simple: true
  }
}

const config_emoji = {
  dataset: 'emoji',
  train_split: 13500,
  dims: [4, 8, 16, 32, 64, 128, 256, 512, 1024],
  schema: {
    'meta': ['i','name', 'mean_color', 'category', 'platform', 'version', 'codepoints', 'shortcode']
  },
  rendering: {
    image: true,
    ext: 'png',
  },
  search: {
    simple: false,
    by: ['name', 'codepoints', 'shortcode'],
    filter: 'platform'
  }
}

const config_glove = {
  dataset: 'glove_6b',
  train_split: 10000,
  dims: [50, 100, 200, 300],
  schema: {
    'meta': ['i', 'name']
  },
  rendering: {
    image: false
  },
  search: {
    simple: true
  }
}

/**
 * Toggle dataset here!
 */
let CONFIG = config_glove

const DEBUG = process.env.NODE_ENV === 'development'
const DATASET = CONFIG.dataset
const TRAIN_SPLIT = CONFIG.train_split

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

/**
 * Global event bus.
 */
let bus = new Vue()

export {
  DEBUG,
  CONFIG,
  DATASET,
  TRAIN_SPLIT,
  store,
  bus,
  log_debug
}

