<template>
  <div>
    <header class="navbar bd-navbar">
      <span class="ml-3" style="font-weight: 500;">Latent Space Explorer</span>
    </header>
    <div v-if="loading"
         class="loading-block d-flex align-items-center justify-content-center">
      <div class="card w-25 h-25">
        <div class="card-body d-flex align-items-center">
          <vue-loading type="spiningDubbles" color="#4b2e83"
                       :size="{ width: '50px', height: '50px' }"></vue-loading>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-9 pr-0">
        <div class="row mr-0">
          <!--Left Panel-->
          <div class="col-4  bd-left">

            <!--Details of a Logo-->
            <div class="card mb-3" v-if="detail_point">
              <div class="card-header">Details</div>
              <div class="card-body">
                <p>{{detail_point.name}}</p>
                <div class="d-flex" style="font-size: 0.8em;">
                  <div class="p1">
                    <img :src="imageUrl(detail_point)" />
                  </div>
                  <div class="w-100 ml-2">
                    <div class="mb-2">
                      <b>Industry: </b>
                      {{detail_point.industry}}
                    </div>
                    <div class="mb-2">
                      <b>Data Source: </b>
                      {{detail_point.source}}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!--List of Brushed Points-->
            <div class="card mb-3" v-if="brushed.length">
              <div class="card-header">Brushed</div>
              <div class="p-2">
                <div v-for="p in brushed" :key="p.i"
                     @click="setDetail(p)"
                     @mouseover="onHighlight(p.i)"
                     @mouseout="onHighlight()"
                     class="bd-point-item d-flex flex-row justify-content-between">
                  <div class="text-truncate">
                    <img :src="imageUrl(p)" class="m-1"/>
                    <span>{{p.name}}</span>
                  </div>
                  <div class="pl-2 d-flex align-items-center">
                    <button class="close" style="font-size:1em;" @click.stop="addOne(p)">
                      <i class="fa fa-plus"></i>
                    </button>
                  </div>
                </div>
                <button class="btn-block btn btn-light mt-3 mb-2"
                        @click="addAll()">Add All</button>
              </div>
            </div>
          </div>

          <!--Main Drawing-->
          <div class="col-8 pr-0 pl-0">
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
            <b-dropdown :text="`Latent Dimensions: ${dim}`" variant="light">
              <b-dropdown-item v-for="d in all_dims" @click="changeDim(d)" :key="d">
                {{d}}
              </b-dropdown-item>
            </b-dropdown>
            <b-dropdown :text="`Projection: ${projection}`" variant="light" class="ml-2">
              <b-dropdown-item v-for="pr in all_projections" :key="pr" @click="changeProjection(pr)">
                {{pr}}
              </b-dropdown-item>
            </b-dropdown>
            <b-dropdown :text="`Perplexity: ${perplexity}`" variant="light" class="ml-2"
                        v-if="projection === 't-SNE'">
              <b-dropdown-item v-for="perp in all_perplexity" @click="changePerp(perp)" :key="perp">
                {{perp}}
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </div>
      </div>

      <!--Right Panel-->
      <div class=" bd-right col-3">
        <search-panel :points="suggestions"
                      v-on:detail="setDetail"
                      v-on:highlight="onHighlight"
                      v-on:reproject="reproject"
                      v-on:original="showOriginal"
                      v-on:subset="onToggleSubset"></search-panel>
      </div>
    </div>
  </div>
</template>

<script>
  import SearchPanel from '../layouts/SearchPanel.vue'
  import ChartButtons from '../layouts/ChartButtons.vue'
  import Scatter from '../controllers/scatter_analogy'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'
  import VueLoading from 'vue-loading-template'

  function clear () {
    // remove all nodes
    let myNode = document.getElementById("container")
    while (myNode.firstChild) {
      myNode.removeChild(myNode.firstChild)
    }

    // reset data
    this.brushed = []
    this.detail_point = null
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
    s.axis = false

    s.drag = false
    s.hover = true
  }

  /**
   * Wrap the draw function
   * @param points
   */
  function lets_draw (points) {
    clear.call(this)
    this.scatter.setData(_.slice(points, 0, TRAIN_SPLIT))
//    scatter.setData(_.slice(points, 0, 1000)) //fixme
    this.scatter.draw('#container')
  }

  function lets_load (callback) {
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

  /**
   * Helper function, looking up the points array for a point with matching index.
   * @param i
   * @param points
   */
  function indexToPoint (i, points) {
    return _.find(points, (p) => p.i === i)
  }

  export default {
    components: {
      SearchPanel,
      ChartButtons,
      VueLoading
    },
    name: 'AnalogyPage',
    data () {
      return {
        scatter: new Scatter(),
        suggestions: [],
        points: [],
        detail_point: null,
        brushed: [],
        dim: 32,
        all_dims: [32, 64, 128, 256, 512, 1024],
        projection: 't-SNE',
        all_projections: ['PCA', 't-SNE'],
        perplexity: 30,
        all_perplexity: [5, 10, 30, 50, 100],
        loading: true,
        night: false,
        err: ''
      }
    },
    mounted: function () {
      // register all the callback of the D3 component
      customize_scatter.call(this, this.scatter)
      this.scatter.onSelected = (pts) => {
        this.brushed = pts
      }
      this.scatter.onDotClicked = (pt) => {
        this.detail_point = pt
      }

      // Get points from server
      lets_load.call(this, () => {
        // set only once, since what really matters is the meta
        this.suggestions = store.meta
      })
    },
    methods: {
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      },

      // change latent dimensions
      changeDim (dim) {
        this.dim = dim
        lets_load.call(this, () => {
          this.scatter.mark_type = 1
        })
      },

      // change projection method
      changeProjection (proj) {
        this.projection = proj
        lets_load.call(this, () => {
          this.scatter.mark_type = 1
        })
      },

      // change perplexity of t-SNE
      changePerp (perp) {
        this.perplexity = perp
        lets_load.call(this, () => {})
      },

      // redo PCA using only selected points
      reproject (indices) {
        this.loading = true
        store.customPca(this.dim, indices)
          .then((points) => {
            this.loading = false
            this.points = points
            this.scatter.mark_type = 2
            log_debug(points)
            lets_draw.call(this, points)
          }, (e) => {
            this.err = e
            this.loading = false
          })
      },

      // change the content of details card
      setDetail (p) {
        this.detail_point = p
      },

      // Add brushed points to the selected list
      addOne (p) {
        if (!_.includes(store.selected, p.i)) {
          store.selected.push(p.i)
        }
      },
      addAll () {
        _.each(this.brushed, (p) => this.addOne(p))
      },

      /**
       * Ugly way to hook up outside DOM event with d3
       * @param i
       */
      onHighlight (i) {
        this.scatter.focusDot(indexToPoint(i, this.points))
      },

      // FIXME: new points won't appear
      onToggleSubset (indices) {
        let pts = indices ? _.map(indices, (i) => indexToPoint(i, this.points)) : null
        this.scatter.focusSet(pts)
      },

      // draw original
      showOriginal () {
        // too lazy to rewrite ...
        this.changeDim(this.dim)
      }
    }
  }
</script>

<style>
  .bd-navbar {
    color: #fff;
    min-height: 4rem;
    background-color: #4b2e83;
    box-shadow: 0 0.5rem 1rem rgba(0,0,0,.05), inset 0 -1px 0 rgba(0,0,0,.1);
  }

  . {
    position: sticky;
    top: 4rem;
    z-index: 1000;
    height: calc(100vh - 4rem);
  }

  .bd-left {
    /*border-right: 1px solid rgba(0,0,0,.1);*/
    height: calc(100vh - 8.56rem) !important;
    overflow-y: auto;
  }

  .bd-right {
    border-left: 1px solid rgba(0,0,0,.1);
    background-color: #fafafa;
    padding-left: 0;
  }

  /*dealing with SVG*/
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

  .focus-label {
    font-size: 20px;
    font-weight: 500;
  }

  .brushed-img {
    width: 32px;
    height: 32px;
  }

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
</style>
