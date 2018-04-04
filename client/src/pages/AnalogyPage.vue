<template>
  <div>
    <header class="navbar bd-navbar">
      <span class="ml-3">Latent Space Explorer</span>
    </header>
    <div class="row">
      <div class="bd-sidebar bd-left col-2"></div>
      <div class="col-7">
        <div class="d-flex justify-content-center align-items-center">
          <div id="container" class="mt-3"></div>
        </div>
      </div>
      <div class="bd-sidebar bd-right col-3">
        <search-panel :points="all_points" v-on:highlight="onHighlight"
                      class="mt-3 mr-3"></search-panel>
      </div>
    </div>
  </div>
</template>

<script>
  import SearchPanel from '../layouts/SearchPanel.vue'
  import Scatter from '../controllers/scatter_pca'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'

  // PCA plot of all points
  let scatter = create_scatter()

  function clear () {
    // remove all nodes
    let myNode = document.getElementById("container")
    while (myNode.firstChild) {
      myNode.removeChild(myNode.firstChild)
    }
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
    clear()
    scatter.setData(_.slice(points, 0, 500))
    scatter.draw('#container')
  }

  export default {
    components: {SearchPanel},
    name: 'AnalogyPage',
    data () {
      return {
        all_points: [],
        dim: 32,
        all_dims: [32, 64, 128, 256, 512, 1024],
        err: ''
      }
    },
    mounted: function () {
      store.getPcaPoints(this.dim)
        .then((points) => {
          // set only once, since what really matters is the meta
          log_debug(points[0])
          this.all_points = points
          lets_draw.call(this, points)
        }, (e) => {
          this.err = e
        })
    },
    methods: {
      /**
       * Ugly way to hook up outside DOM event with d3
       * @param p
       */
      onHighlight (p) {
        scatter.focusDot(p)
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
    background-color: #fafafa;
    height: calc(100vh - 4rem);
  }

  .bd-left {
    border-right: 1px solid rgba(0,0,0,.1);
  }

  .bd-right {
    border-left: 1px solid rgba(0,0,0,.1);
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
</style>
