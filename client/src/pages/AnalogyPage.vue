<template>
  <div>
    <header class="navbar bd-navbar">
      <span class="ml-3">Latent Space Explorer</span>
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
      <!--Left Panel-->
      <div class="col-3 bd-sidebar bd-left">

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
                 @mouseover="onHighlight(p)"
                 @mouseout="onHighlight()"
                 class="bd-point-item d-flex flex-row justify-content-between">
              <div class="text-truncate">
                <img :src="imageUrl(p)" class="m-1"/>
                <span>{{p.name}}</span>
              </div>
              <div class="pl-2 d-flex align-items-center">
                <button class="close" style="font-size:1em;" @click.stop="">
                  <i class="fa fa-plus"></i>
                </button>
              </div>
            </div>
            <button class="btn-block btn btn-light mt-3 mb-2"
                    @click="">Add All</button>
          </div>
        </div>
      </div>

      <!--Main Drawing-->
      <div class="col-6">
        <div class="d-flex justify-content-center align-items-center">
          <div id="container" class="mt-3"></div>
        </div>
      </div>

      <!--Right Panel-->
      <div class="bd-sidebar bd-right col-3">
        <search-panel :points="all_points"
                      v-on:detail="setDetail"
                      v-on:highlight="onHighlight"
                      v-on:subset="onToggleSubset"></search-panel>
      </div>
    </div>
  </div>
</template>

<script>
  import SearchPanel from '../layouts/SearchPanel.vue'
  import Scatter from '../controllers/scatter_pca'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'
  import VueLoading from 'vue-loading-template'

  // PCA plot of all points
  let scatter = create_scatter()

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

  function create_scatter () {
    let s = new Scatter()
    s.outerWidth = 600
    s.outerHeight = 600
    s.margin = {
      top: 15,
      bottom: 15,
      left: 15,
      right: 15
    }
    s.dot_radius = 3
    s.axis = false

    s.drag = false
    s.hover = true

    return s
  }

  /**
   * Wrap the draw function
   * @param points
   */
  function lets_draw (points) {
    clear.call(this)
    scatter.setData(_.slice(points, 0, TRAIN_SPLIT))
    scatter.draw('#container')
  }

  export default {
    components: {
      SearchPanel,
      VueLoading
    },
    name: 'AnalogyPage',
    data () {
      return {
        all_points: [],
        detail_point: null,
        brushed: [],
        dim: 32,
        all_dims: [32, 64, 128, 256, 512, 1024],
        loading: true,
        err: ''
      }
    },
    created: function () {
      // register all the callback of the D3 component
      scatter.onSelected = (pts) => {
        this.brushed = pts
      }
      scatter.onDotClicked = (pt) => {
        this.detail_point = pt
      }
    },
    mounted: function () {
      this.loading = true
      store.getPcaPoints(this.dim)
        .then((points) => {
          this.loading = false
          log_debug(points[0])
          // set only once, since what really matters is the meta
          this.all_points = points
          lets_draw.call(this, points)
        }, (e) => {
          this.err = e
          this.loading = false
        })
    },
    methods: {
      imageUrl (p) {
        return store.getImageUrl(p.i)
      },
      setDetail (p) {
        this.detail_point = p
      },
      /**
       * Ugly way to hook up outside DOM event with d3
       * @param p
       */
      onHighlight (p) {
        scatter.focusDot(p)
      },
      onToggleSubset (pts) {
        scatter.focusSet(pts)
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

  .bd-sidebar {
    position: sticky;
    top: 4rem;
    z-index: 1000;
    height: calc(100vh - 4rem);
  }

  .bd-left {
    /*border-right: 1px solid rgba(0,0,0,.1);*/
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
</style>
