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
  import {draw, setData, setCb, setPca} from '../controllers/scatter_pca'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'

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

  export default {
    name: 'ScatterPage',
    data () {
      return {
        dim: 32,
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
      setCb((images) => {
        this.images = images
      })
      setPca((x, y, i) => {
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
      })
    },
    mounted: function () {
      store.getPcaPoints(this.dim)
        .then((points) => {
          setData(_.slice(points, TRAIN_SPLIT))
          this.variation = store.getPcaVarSync(this.dim)
          log_debug(points[0])
          draw('#container')
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
            setData(_.slice(points, TRAIN_SPLIT))
            this.variation = store.getPcaVarSync(this.dim)
            draw('#container')
          }, (e) => {
            this.err = e
          })
      },
      changeData (str) {
        clear.call(this)

        let points = store.getPcaPointsSync(this.dim)

        if (/test/i.test(str)) {
          setData(_.slice(points, TRAIN_SPLIT))
        } else if (/train/i.test(str)) {
          setData(_.slice(points, 0, TRAIN_SPLIT))
        } else {
          setData(points)
        }

        draw('#container')
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

  .d3-tip {
    line-height: 1;
    font-weight: bold;
    padding: 12px;
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
    border-radius: 2px;
  }

  /* Creates a small triangle extender for the tooltip */
  .d3-tip:after {
    box-sizing: border-box;
    display: inline;
    font-size: 10px;
    width: 100%;
    line-height: 1;
    color: rgba(0, 0, 0, 0.8);
    content: "\25BC";
    position: absolute;
    text-align: center;
  }

  /* Style northward tooltips differently */
  .d3-tip.n:after {
    margin: -1px 0 0 0;
    top: 100%;
    left: 0;
  }

  .highlight {
    fill-opacity: 1;
    stroke: red;
    stroke-width: 2px;
  }
</style>
