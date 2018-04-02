<template>
  <div class="row mt-5">
    <div class="col-2"></div>
    <div class="col-8 text-center">
      <h3 class="mb-3">PCA of Latent Space</h3>
      The first two principal components account for {{formatVar(variation[0])}} and
      {{formatVar(variation[1])}} of the variation, respectively.
      <div id="container" class="mt-3"></div>

      <!--buttons-->
      <div class="text-left">
        <b-dropdown text="Latent Dimensions" class="m-2">
          <b-dropdown-item v-for="d in all_dims" @click="changeDim(d)">
            {{d}}
          </b-dropdown-item>
        </b-dropdown>
        <b-dropdown text="Data" class="m-2">
          <b-dropdown-item v-for="c in all_data_choices" @click="changeData(c)">
            {{c}}
          </b-dropdown-item>
        </b-dropdown>
        <span class="pull-right text-muted" v-if="recon_loading">
          computing...
        </span>
        <img :src="recon" v-if="recon" class="pull-right"/>
      </div>

      <!--images-->
      <div class="text-left mt-3">
        <div v-if="images.length" class="pb-3">
          <hr>
        </div>
        <span v-for="img in images">
          <img :src="img"/>
        </span>
      </div>
    </div>
    <div class="col-2"></div>
  </div>
</template>

<script>
  import Scatter from '../controllers/scatter_pca'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'

  let scatter = new Scatter()

  function clear () {
    // remove all nodes
    let myNode = document.getElementById("container")
    while (myNode.firstChild) {
      myNode.removeChild(myNode.firstChild)
    }

    // reset data
    this.images = []
    this.recon = null
  }

  /**
   * Based on the option, slice the data array differentially to be a subset.
   * @param points An array of points, passed by reference
   * @param option Slicing option
   */
  function sliceData (points, option) {
    if (option === 0) {
      scatter.setData(_.slice(points, TRAIN_SPLIT))
    } else if (option === 1) {
      scatter.setData(_.slice(points, 0, TRAIN_SPLIT))
    } else {
      scatter.setData(points)
    }
  }

  /**
   * Wrap the draw function
   * @param points
   */
  function lets_draw (points) {
    sliceData(points, this.data_slice)
    this.variation = store.getPcaVarSync(this.dim)
    scatter.draw('#container')
  }

  export default {
    name: 'ScatterPage',
    data () {
      return {
        dim: 32,
        data_slice: 0,
        recon: null,
        recon_loading: false,
        variation: [],
        images: [],
        all_dims: [32, 64, 128, 256, 512, 1024],
        all_data_choices: ['Test Set', 'Training Set', 'All'],
        err: ''
      }
    },
    created: function () {
      scatter.onSelected = (pts) => {
        this.images = _.map(pts, (p) => store.getImageUrl(p.i))
      }
      scatter.onProbed = (x, y, i) => {
        this.recon = null
        this.recon_loading = true
        store.transformPoint(x, y, i)
          .then((img) => {
            log_debug(img)
            this.recon = '/build/' + img
            this.recon_loading = false
          }, (e) => {
            log_debug(e)
            this.recon_loading = false
          })
      }
    },
    mounted: function () {
      store.getPcaPoints(this.dim)
        .then((points) => {
          lets_draw.call(this, points)
        }, (e) => {
          this.err = e
        })
    },
    methods: {
      changeDim (dim) {
        this.dim = dim

        clear.call(this)

        store.getPcaPoints(this.dim)
          .then((points) => {
            lets_draw.call(this, points)
          }, (e) => {
            this.err = e
          })
      },
      changeData (str) {
        clear.call(this)

        let points = store.getPcaPointsSync(this.dim)

        if (/test/i.test(str)) {
          this.data_slice = 0
        } else if (/train/i.test(str)) {
          this.data_slice = 1
        } else {
          this.data_slice = 2
        }

        lets_draw.call(this, points)
      },
      formatVar (v) {
        if (!v) {
          return '0%'
        }
        return `${(Number(v) * 100).toFixed(2)}%`
      }
    }
  }
</script>

<style>
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
