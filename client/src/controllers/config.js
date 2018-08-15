import Store from '../controllers/store'
import Vue from 'vue'

const DTYPE = {
  numeric: 'numeric',
  categorical: 'categorical'
}

const config_logo = {
  dataset: 'logo',
  date_type: 'image',
  train_split: 15000,
  dims: [32, 64, 128, 256, 512, 1024],
  schema: {
    'meta': ['i', 'name', 'mean_color', 'source', 'industry']
  },
  rendering: {
    dot_color: 'mean_color',
    ext: 'jpg',
  },
  search: {
    simple: true
  }
}

const config_emoji = {
  dataset: 'emoji',
  data_type: 'image',
  train_split: 13500,
  dims: [4, 8, 16, 32, 64, 128, 256, 512, 1024],
  schema: {
    'meta': ['i','name', 'mean_color', 'category', 'platform', 'version', 'codepoints', 'shortcode']
  },
  rendering: {
    dot_color: 'mean_color',
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
  data_type: 'text',
  train_split: 10000,
  dims: [50, 100, 200, 300],
  schema: {
    'meta': ['i', 'name']
  },
  rendering: {
    dot_color: null
  },
  search: {
    simple: true
  }
}

const config_tybalt = {
  dataset: 'tybalt',
  data_type: 'other',
  train_split: 10458,
  dims: [100],
  schema: {
    'type': {
      'y': DTYPE.numeric,
      'organ': DTYPE.categorical,
      'stage': DTYPE.categorical,
      'gender': DTYPE.categorical,
      'age_at_diagnosis': DTYPE.numeric
    },
    'meta': ['i', 'name', 'platform', 'age_at_diagnosis', 'race', 'stage', 'vital_status',
      'disease', 'organ', 'gender', 'analysis_center', 'year_of_diagnosis',
      'ovarian_cancer_subtype'],
    'header': ['i', 'gene']
  },
  rendering: {
    dot_color: 'organ'
  },
  search: {
    simple: false,
    by: ['name'],
    filter: 'stage'
  },
  color_by: ['organ', 'race', 'stage', 'vital_status', 'gender',
    'analysis_center', 'ovarian_cancer_subtype'],
  y_axis: ['y', 'organ', 'race', 'stage', 'gender', 'age_at_diagnosis',
    'ovarian_cancer_subtype']
}

/**
 * Toggle dataset here!
 */
let CONFIG = config_tybalt

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
  DTYPE,
  DATASET,
  TRAIN_SPLIT,
  store,
  bus,
  log_debug
}

