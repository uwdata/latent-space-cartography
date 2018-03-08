<template>
  <div class="row mt-5">
    <div class="col-2"></div>
    <div class="col-8 text-center">
      <h3 class="mb-3">Some Title.</h3>
      This is a description.
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
  import {draw, setData, setCb} from '../controllers/scatter'
  import {store, log_debug, TRAIN_SPLIT} from '../controllers/config'
  import _ from 'lodash'

  function clear () {
    // remove all nodes
    let myNode = document.getElementById("container")
    while (myNode.firstChild) {
      myNode.removeChild(myNode.firstChild)
    }
  }

  export default {
    name: 'ScatterPage',
    data () {
      return {
        dim: 32,
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
    },
    mounted: function () {
      store.getPoints(this.dim)
        .then((points) => {
          setData(_.slice(points, TRAIN_SPLIT))
          draw('#container')
        }, (e) => {
          this.err = e
        })
    },
    methods: {
      changeDim (dim) {
        this.dim = dim
        this.images = []

        clear()

        store.getPoints(this.dim)
          .then((points) => {
            setData(_.slice(points, TRAIN_SPLIT))
            draw('#container')
          }, (e) => {
            this.err = e
          })
      },
      changeData (str) {
        this.images = []
        clear()

        let points = store.pca[this.dim]

        if (/test/i.test(str)) {
          setData(_.slice(points, TRAIN_SPLIT))
        } else if (/train/i.test(str)) {
          setData(_.slice(points, 0, TRAIN_SPLIT))
        } else {
          setData(points)
        }

        draw('#container')
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
    fill-opacity: .5;
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
</style>
