<template>
  <div class="bd-outer">
    <!--Search Panel-->
    <search-panel :open="open_search" :button="$refs.btnSearch" :meta="suggestions"
                  v-on:close="open_search=false" v-if="show_search"></search-panel>

    <!--Header-->
    <header class="navbar bd-navbar">
      <span class="ml-3" style="font-weight: 500;">Latent Space Cartography</span>
      <help-button class="ml-3"></help-button>
    </header>

    <!--Loading Spinner-->
    <div v-if="loading"
         class="loading-block d-flex align-items-center justify-content-center">
      <div class="card w-25 h-25">
        <div class="card-body d-flex align-items-center">
          <vue-loading type="spiningDubbles" color="#4b2e83"
                       :size="{ width: '50px', height: '50px' }"></vue-loading>
        </div>
      </div>
    </div>

    <!--Main View-->
    <div class="row">
      <!--Detail Tooltip -->
      <detail-tip></detail-tip>

      <div class="col-9 pr-0">
        <div class="mr-0">
          <!--Left Panel-->
          <div class="bd-left ml-2">
            <!--Detail Card-->
            <detail-card :latent_dim="dim"></detail-card>

            <!--List of Brushed Points-->
            <brushed-list :chart="scatter" :brushed="brushed"></brushed-list>
          </div>

          <!--Main Drawing-->
          <div class="pr-0 pl-0">
            <div class="d-flex justify-content-center align-items-center">
              <!--SVG-->
              <div id="container" ref="chart"></div>

              <!--Buttons-->
              <chart-buttons :chart="scatter" v-on:reset="showOriginal"></chart-buttons>
            </div>
          </div>
        </div>

        <!--Footer-->
        <div class="bd-app-footer">
          <div class="m-3 text-left">
            <button class="btn btn-light" @click="open_search=true" ref="btnSearch" v-if="show_search">
              <i class="fa fa-fw fa-search"></i>
            </button>
            <b-dropdown :text="`Latent Dimensions: ${dim}`" variant="light" class="ml-2">
              <b-dropdown-item v-for="d in all_dims" @click="changeDim(d)" :key="d">
                {{d}}
              </b-dropdown-item>
            </b-dropdown>
            <b-dropdown :text="`Projection: ${projection}`" variant="light" class="ml-2"
                        v-if="view_state===0">
              <b-dropdown-item v-for="pr in all_projections" :key="pr" @click="changeProjection(pr)">
                {{pr}}
              </b-dropdown-item>
            </b-dropdown>
            <b-dropdown :text="`Perplexity: ${perplexity}`" variant="light" class="ml-2"
                        v-if="projection === 't-SNE' && view_state === 0">
              <b-dropdown-item v-for="perp in all_perplexity" @click="changePerp(perp)" :key="perp">
                {{perp}}
              </b-dropdown-item>
            </b-dropdown>

            <!--On the right-->
            <div v-if="all_color.length" class="float-right ml-2">
              <b-dropdown :text="`Color By: ${prettyName(current_color)}`" variant="light">
                <b-dropdown-item v-for="c in all_color" @click="changeColor(c)" :key="c">
                  {{prettyName(c)}}
                </b-dropdown-item>
              </b-dropdown>
            </div>
            <div v-if="all_y.length" class="float-right ml-2">
              <b-dropdown :text="`Y-Axis: ${prettyName(current_y)}`" variant="light">
                <b-dropdown-item v-for="y in all_y" @click="changeYAxis(y)" :key="y">
                  {{prettyName(y)}}
                </b-dropdown-item>
              </b-dropdown>
            </div>
            <div v-if="all_x.length" class="float-right ml-2">
              <b-dropdown :text="`X-Axis: ${prettyName(current_x)}`" variant="light">
                <b-dropdown-item v-for="x in all_x" @click="changeXAxis(x)" :key="x">
                  {{prettyName(x)}}
                </b-dropdown-item>
              </b-dropdown>
            </div>
            <filter-dropdown :meta="suggestions"
                             v-on:filter="onFilter"></filter-dropdown>
            <filter-button :meta="suggestions" v-if="show_filter"
                           v-on:filter="onFilter"></filter-button>
          </div>
        </div>
      </div>

      <!--Right Panel-->
      <div class=" bd-right col-3">
        <group-panel :points="suggestions" :view_state="view_state" :latent_dim="dim"
                     v-on:center="onCenter"
                     v-on:highlight="onHighlight"
                     v-on:reproject="reproject"
                     v-on:original="showOriginal"></group-panel>
        <vector-panel :latent_dim="dim" :chart="scatter" :view_state="view_state"
                      v-on:focus="focusVector" :proj_state="proj_state"
                      v-on:reset="showOriginal"></vector-panel>
      </div>
    </div>
  </div>
</template>

<script>
  import GroupPanel from '../layouts/GroupPanel.vue'
  import VectorPanel from '../layouts/VectorPanel.vue'
  import ChartButtons from '../layouts/ChartButtons.vue'
  import HelpButton from '../layouts/HelpButton.vue'
  import InterpolatePanel from '../layouts/InterpolatePanel.vue'
  import DetailCard from '../layouts/DetailCard.vue'
  import DetailTip from '../layouts/DetailTip.vue'
  import BrushedList from '../layouts/BrushedList.vue'

  import Scatter from '../controllers/scatter_analogy'
  import {store, bus, log_debug, CONFIG, DTYPE} from '../controllers/config'
  import _ from 'lodash'
  import VueLoading from 'vue-loading-template'
  import FilterDropdown from '../layouts/FilterDropdown.vue'
  import SearchPanel from '../layouts/SearchPanel.vue'
  import FilterButton from '../layouts/FilterButton.vue'

  function clear () {
    // remove all nodes
    let myNode = document.getElementById("container")
    while (myNode.firstChild) {
      myNode.removeChild(myNode.firstChild)
    }

    // reset data
    this.brushed = []
    store.state.detail = null
  }

  // Customize the style of scatter plot
  function customize_scatter (s) {
    s.outerWidth = this.$refs.chart.clientWidth
    s.outerHeight = this.$refs.chart.clientHeight
    s.margin = {
      top: 0,
      bottom: 0,
      left: 0,
      right: 0
    }
    s.dot_radius = 3
    s.dot_color = CONFIG.rendering.dot_color
    s.mark_type = CONFIG.data_type === 'text' ? 3 : CONFIG.data_type === 'image' ? 2 : 1
  }

  /**
   * Helper function, looking up the points array for a point with matching index.
   * @param i
   * @param points
   */
  function indexToPoint (i, points) {
    return _.find(points, (p) => p.i === i)
  }

  function indicesToPoint (is, points) {
    let map = {}
    _.each(points, (p) => {
      map[p.i] = p
    })
    return _.map(is, (i) => map[i])
  }

  // a hack to wrangle Google's analogy test set
  // FIXME: remove this
  function wrangle (input) {
    input = input.split('\n')
    let dict = _.keyBy(store.meta, 'name')
    let left = _.map(input, (line) => _.toLower(line.split(' ')[2]))
    let right = _.map(input, (line) => _.toLower(line.split(' ')[3]))
    let il = _.filter(_.map(left, (w, idx) => w in dict ? idx : -1), (i) => i >= 0)
    let ir = _.filter(_.map(right, (w, idx) => w in dict ? idx : -1), (i) => i >= 0)
    let valid = _.keyBy(_.intersection(il, ir))
    left = _.filter(left, (w, i) => i in valid)
    right = _.filter(right, (w, i) => i in valid)
    console.log(left.join(','))
    console.log(right.join(','))
  }

  /**
   * Wrap the draw function
   * @param points
   */
  function lets_draw (points) {
    clear.call(this)
    // points = _.slice(points, 0, 999)
    points = _.slice(points, 0, CONFIG.train_split)
    let active = this.filter_func(points)
    this.scatter.setData(active)
    this.scatter.draw('#container')
  }

  function lets_load (callback) {
    this.view_state = 0

    // reset chart style
    this.scatter.chart_type = 1
    resetAxes.call(this)

    clear.call(this)
    this.loading = true
    let func = this.projection === 't-SNE' ? store.getTsnePoints : store.getPcaPoints
    let args = [this.dim]
    if (this.projection === 't-SNE') {
      args.push(this.perplexity)
    }

    func.call(store, ...args)
      .then((points) => {
        this.loading = false
        this.points = points
        callback()
        lets_draw.call(this, points)
      }, (e) => {
        this.err = e
        this.loading = false
      })
  }

  function resetAxes () {
    this.current_y = 'y'
    this.current_x = 'x'
    this.scatter.y_field = this.current_y
    this.scatter.x_field = this.current_x
  }

  export default {
    components: {
      FilterButton,
      SearchPanel,
      FilterDropdown,
      BrushedList,
      GroupPanel,
      VectorPanel,
      ChartButtons,
      HelpButton,
      InterpolatePanel,
      DetailCard,
      DetailTip,
      VueLoading
    },
    name: 'AnalogyPage',
    data () {
      return {
        scatter: new Scatter(),
        suggestions: [],
        points: [],
        brushed: [],
        view_state: 0, // 0 - main, 1 - subset PCA, 2 - vector PCA
        all_dims: CONFIG.dims,
        dim: CONFIG.dims[0],
        projection: 't-SNE',
        all_projections: ['PCA', 't-SNE'],
        perplexity: 30,
        all_perplexity: [5, 10, 30, 50, 100],
        current_color: CONFIG.rendering.dot_color,
        all_color: CONFIG.color_by || [],
        current_x: 'x',
        current_y: 'y',
        filter_func: (d) => d,
        show_search: !CONFIG.search.simple,
        open_search: false,
        show_filter: CONFIG.filter,
        loading: true,
        err: ''
      }
    },
    watch: {
      view_state () {
        resetAxes.call(this)
      }
    },
    computed: {
      proj_state: function () {
        let code = this.view_state === 0 ? this.projection :
          this.view_state === 1 ? 'subset' : 'vector'
        if (code === 't-SNE') {
          code = 'tsne-' + this.perplexity
        }
        code += `-dim${this.dim}`
        return _.toLower(code)
      },
      all_y: function () {
        if (this.view_state === 0 && this.projection === 'PCA') {
          return _.map(_.range(4), (j) => `PC${j + 1}`)
        }
        if (this.view_state === 2) {
          return CONFIG.y_axis || []
        }
        return []
      },
      all_x: function () {
        if (this.view_state === 0 && this.projection === 'PCA') {
          return _.map(_.range(4), (j) => `PC${j + 1}`)
        }
        return []
      }
    },
    mounted: function () {
      // register all the callback of the D3 component
      customize_scatter.call(this, this.scatter)
      this.scatter.emitter.onSelected = (pts) => {
        this.brushed = pts
      }
      this.scatter.emitter.onDotClicked = (pt, shift) => {
        if (!shift) {
          // 1. normal click brings up detail
          store.state.detail_card = pt
          if (CONFIG.data_type === 'text' && this.view_state === 2) {
            store.state.detail_card = null // hack: don't show card in vector view
          }
          store.state.clicked_point = pt
        } else {
          // 2. shift + click adds a point to the current group
          store.state.detail_card = null
          store.state.clicked_point = null
          store.selected.push(pt.i)
        }
      }
      this.scatter.emitter.onDotHovered = (pt, x, y) => {
        if (pt) {
          pt.clientX = x
          pt.clientY = y
        }
        store.state.detail = pt
      }

      // register event
      bus.$on('highlight-subset', this.onToggleSubset)

      // Get points from server
      lets_load.call(this, () => {
        // set only once, since what really matters is the meta
        this.suggestions = store.meta

        // broadcast that the main chart has been initialized
        bus.$emit('chart-ready')
      })
    },
    methods: {
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      },
      prettyName (text) {
        if (!text)  return ''

        // hard-code default axis name
        if (text === 'y') {
          if (this.view_state === 2) return 'PC1'
          if (this.view_state === 0 && this.projection === 't-SNE') return 'Default'
          return 'PC2'
        }
        if (text === 'x' && this.view_state === 0 && this.projection === 'PCA') {
          return 'PC1'
        }

        // only make the first letter of each word uppercase
        let words = _.map(text.split('_'), (w) => _.toUpper(w[0]) + w.substr(1))
        return words.join(' ')
      },

      // change the y axis
      changeYAxis (y) {
        this.current_y = y
        let type = CONFIG.schema.type
        if (type[y] === DTYPE.categorical) {
          this.scatter.chart_type = 2
        } else {
          // assume numeric by default
          this.scatter.chart_type = 1
        }

        this.scatter.y_field = y
        lets_draw.call(this, this.points)
      },

      // change the x axis
      changeXAxis (x) {
        this.current_x = x
        this.scatter.x_field = x
        lets_draw.call(this, this.points)
      },

      // change the color by
      changeColor (c) {
        this.current_color = c
        this.scatter.dot_color = c
        lets_draw.call(this, this.points)
      },

      // change latent dimensions
      changeDim (dim) {
        this.dim = dim
        lets_load.call(this, () => {})
      },

      // change projection method
      changeProjection (proj) {
        this.projection = proj
        lets_load.call(this, () => {})
      },

      // change perplexity of t-SNE
      changePerp (perp) {
        this.perplexity = perp
        lets_load.call(this, () => {})
      },

      // redo PCA using only selected points
      reproject (indices) {
        this.loading = true
        this.view_state = 1
        store.customPca(this.dim, indices)
          .then((points) => {
            this.loading = false
            this.points = points
            log_debug(points)
            lets_draw.call(this, points)
          }, (e) => {
            this.err = e
            this.loading = false
          })
      },

      focusVector (vector) {
        this.loading = true
        this.view_state = 2
        store.focusVector(this.dim, vector.start, vector.end)
          .then((all) => {
            // 1. draw points
            let points = all[0]
            this.loading = false
            this.points = points
            lets_draw.call(this, points)

            // 2. draw line
            vector.line = all[1]
            vector.points_start = indicesToPoint(vector.list_start, points)
            vector.points_end = indicesToPoint(vector.list_end, points)
            // points_start and points_end are useful to draw confidence cone
            bus.$emit('draw-focus-vec', vector, all[2])
          }, () => {
            this.loading = false
            //handle error
          })
      },

      onFilter (func) {
        this.filter_func = func
        lets_draw.call(this, this.points)
      },

      /**
       * Ugly way to hook up outside DOM event with d3
       * @param i
       */
      onHighlight (i) {
        this.scatter.focusDot(indexToPoint(i, this.points))
      },
      onCenter (i) {
        this.scatter.centerDot(indexToPoint(i, this.points))
      },

      // FIXME: new points won't appear
      onToggleSubset (indices) {
        let pts = indices ? indicesToPoint(indices, this.points) : null
        this.scatter.focusSet(pts)
      },

      // draw original
      showOriginal () {
        resetAxes.call(this)
        // too lazy to rewrite ...
        this.changeDim(this.dim)
      }
    }
  }
</script>

<style>
  html, body {
    height: 100%;
    overflow: hidden;
  }

  .bd-outer {
    overflow-y:hidden;
    overflow-x:hidden;
  }
  .bd-navbar {
    color: #fff;
    min-height: 4rem;
    background-color: #4b2e83;
    box-shadow: 0 0.5rem 1rem rgba(0,0,0,.05), inset 0 -1px 0 rgba(0,0,0,.1);
  }

  .bd-sidebar {
    position: sticky;
    top: 4rem;
    z-index: 1000;
    height: calc(100vh - 4rem);
  }

  .bd-left {
    position: absolute;
    z-index: 1000;
    top: 0;
    left: 0;
    width: calc(25vw);
    max-height: calc(100vh - 8.56rem) !important;
    overflow-y: auto;
  }

  .bd-right {
    border-left: 1px solid rgba(0,0,0,.1);
    background-color: #fafafa;
    padding-left: 0;
  }

  .bd-subtitle {
    font-size: 0.8em;
    font-weight: 500;
  }

  .text-sm {
    font-size: 0.8em;
  }

  .bd-btn-trans {
    display: inline-block;
    cursor: pointer;
  }
  .bd-btn-trans:hover {
    background-color: #eee;
  }

  /* ------- D3 STYLE START ------- */
  .axis path,
  .axis line {
    fill: none;
    stroke: rgba(0, 0, 0, 0.1);
    shape-rendering: crispEdges;
  }

  .axisLine {
    fill: none;
    shape-rendering: crispEdges;
    stroke: rgba(0, 0, 0, 0.5);
    stroke-width: 2px;
  }

  .dot {
    fill-opacity: .8;
  }
  .dot.muted {
    fill: #ccc !important;
    fill-opacity: .4 !important;
  }

  .legend-mark {
    cursor: pointer;
  }

  .legend-label {
    cursor: pointer;
  }

  .legend-mark.muted {
    fill-opacity: .3;
  }

  .legend-label.muted {
    opacity: .3;
  }

  .outlined-text {
    paint-order: stroke;
    stroke: #fff;
    stroke-width: 2px;
    stroke-linecap: butt;
    stroke-linejoin: miter;
  }

  .focus-label {
    font-size: 20px;
    font-weight: 500;
  }

  .brushed-img {
    width: 32px;
    height: 32px;
  }

  .dot-text {
    font-weight: 300;
  }

  /* ------- D3 STYLE END ------- */

  .loading-block {
    position: absolute;
    left: 0;
    top: 4rem;
    background-color: rgba(0, 0, 0, 0.2);
    z-index: 10000;
    width: 100%;
    height: calc(100vh - 4rem);
  }

  #container {
    width: 100%;
    height: calc(100vh - 8.56rem);
  }

  .bd-app-footer {
    position: sticky;
    bottom: 0;
    height: 4.56em;
    z-index: 1000;
    background-color: #fff;
    border-top: 1px solid rgba(0,0,0,.1);
    box-shadow: 0.5rem 0 2rem rgba(0,0,0,.03);
  }

  .bd-pointer {
    cursor: pointer;
  }
</style>
