import Store from '../controllers/store'
import Vue from 'vue'

const config_logo = {
  dataset: 'logo',
  train_split: 15000,
  ext: 'jpg',
  schema: {
    'meta': ['i', 'name', 'mean_color', 'source', 'industry']
  },
  search: {
    simple: true
  }
}

const config_emoji = {
  dataset: 'emoji',
  train_split: 13500,
  ext: 'png',
  schema: {
    'meta': ['i','name', 'mean_color', 'category', 'platform', 'version', 'codepoints', 'shortcode']
  },
  search: {
    simple: false,
    by: ['name', 'codepoints', 'shortcode'],
    filter: 'platform'
  }
}

/**
 * Toggle dataset here!
 */
let CONFIG = config_emoji

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

