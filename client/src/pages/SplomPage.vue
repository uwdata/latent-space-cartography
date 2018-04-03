<template>
  <div>
    <!--Title-->
    <div class="text-center mt-5">
      <h3 class="mb-3">PCA of the Latent Space</h3>
      Total variation explained: {{`${total_var}%`}}
    </div>
    <div class="row justify-content-center">
      <div class="text-center col-8" style="width: 1000px">
        <div id="container" class="mt-3"></div>

        <!--buttons-->
        <div>
          <b-dropdown :text="`Latent Dimensions: ${dim}`" class="m-2">
            <b-dropdown-item v-for="d in all_dims" @click="changeDim(d)" :key="d">
              {{d}}
            </b-dropdown-item>
          </b-dropdown>
          <b-dropdown :text="`Data: ${all_data_choices[data_slice]}`" class="m-2">
            <b-dropdown-item v-for="c in all_data_choices" @click="changeData(c)" :key="c">
              {{c}}
            </b-dropdown-item>
          </b-dropdown>
        </div>
      </div>
      <!--Side Views-->
      <!--TODO: hardcode-->
      <div class="col-1">
        <div style="margin-top: 40px"></div>
        <div v-for="pc in [0,1,2,3,4,5,6,7]" style="padding-bottom: 20px" class="pl-3">
          <div v-for="j in [2,1,0,-1,-2]" style="height: 20px">
            <img :src="`/data/splom/dim${dim}_pc${pc}_${j}.png`"
                 style="width: 20px; height: 20px;"/>
          </div>
        </div>
      </div>
      <div class="col-3 img-panel" :style="{marginTop: scroll_top + 'px'}">
        <!--images-->
        <div class="text-left mt-5">
        <span v-for="img in images">
          <img :src="img" :style="{ width: img_size + 'px', height: img_size + 'px'}"/>
        </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import Splom from '../controllers/splom'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'

  const PCA_DIM = 8
  let splom = new Splom(PCA_DIM)

  function clear () {
    // remove all nodes
    let myNode = document.getElementById("container")
    while (myNode.firstChild) {
      myNode.removeChild(myNode.firstChild)
    }

    // reset data
    this.images = []
  }

  /**
   * Based on the option, slice the data array differentially to be a subset.
   * @param points An array of points, passed by reference
   * @param option Slicing option
   */
  function sliceData (points, option) {
    if (option === 0) {
//      splom.setData(_.slice(points, TRAIN_SPLIT))
      // TODO: deal with performance issue
      splom.setData(_.slice(points, 18000))
    } else if (option === 1) {
      splom.setData(_.slice(points, 0, TRAIN_SPLIT))
    } else {
      splom.setData(points)
    }
  }

  /**
   * Wrap the draw function
   * @param points
   */
  function lets_draw (points) {
    sliceData(points, this.data_slice)
    let va = store.getPcaVarSync(this.dim)
    splom.variation = va
    this.total_var = (_.sum(va) * 100).toFixed(2)
    splom.draw('#container')
  }

  export default {
    name: 'ScatterPage',
    data () {
      return {
        dim: 32,
        data_slice: 0,
        total_var: 0,
        img_size: 48,
        images: [],
        all_dims: [32, 64, 128, 256, 512, 1024],
        all_data_choices: ['Test Set', 'Training Set', 'All'],
        scroll_top: 0,
        err: ''
      }
    },
    created: function () {
      splom.onSelected = (images) => {
        this.images = images
      }
      window.addEventListener('scroll', this.handleScroll)
    },
    destroyed: function () {
      window.removeEventListener('scroll', this.handleScroll)
    },
    mounted: function () {
      store.getPcaPoints(this.dim, PCA_DIM)
        .then((points) => {
          log_debug(points[0])
          lets_draw.call(this, points)
        }, (e) => {
          this.err = e
        })
    },
    methods: {
      changeDim (dim) {
        this.dim = dim

        clear.call(this)

        store.getPcaPoints(this.dim, PCA_DIM)
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
      handleScroll (event) {
        let y = window.scrollY
        if (y > 400) {
          this.scroll_top = 400
        } else {
          this.scroll_top = 0
        }
      }
    }
  }
</script>

<style>
  svg {
    font: 10px sans-serif;
    padding: 10px;
  }

  .axis,
  .frame {
    shape-rendering: crispEdges;
  }

  .axis line {
    stroke: #ddd;
  }

  .axis path {
    display: none;
  }

  .cell text {
    font-weight: bold;
    text-transform: capitalize;
    fill: #000;
  }

  .frame {
    fill: none;
    stroke: #aaa;
  }

  circle {
    fill-opacity: .8;
  }
  circle.muted {
    fill-opacity: .4 !important;
    fill: #ccc !important;
  }

  .extent {
    fill: #000;
    fill-opacity: .125;
    stroke: #fff;
  }

  .img-panel {
    height: 480px;
    overflow-y: scroll;
  }
</style>
