<template>
  <div class="row justify-content-center mt-5">
    <div class="text-center" style="width: 864px">
      <h3 class="mb-3">t-SNE of the Latent Space</h3>
      You are exploring the {{dim}}-dimensional latent space of a variational auto-encoder
      on a logo database containing 15,000 training samples and 3,656 test samples.
      To generate this plot, we ran t-SNE with perplexity {{perplexity}} for 1,000 iterations.
      <div id="container" class="mt-3"></div>

      <!--buttons-->
      <div>
        <b-dropdown :text="`Latent Dimensions: ${dim}`" class="m-2">
          <b-dropdown-item v-for="d in all_dims" @click="changeDim(d)">
            {{d}}
          </b-dropdown-item>
        </b-dropdown>
        <b-dropdown :text="`Perplexity: ${perplexity}`" class="m-2">
          <b-dropdown-item v-for="perp in all_perplexity" @click="changePerp(perp)">
            {{perp}}
          </b-dropdown-item>
        </b-dropdown>
        <b-dropdown :text="`Data: ${all_data_choices[data_slice]}`" class="m-2">
          <b-dropdown-item v-for="c in all_data_choices" @click="changeData(c)">
            {{c}}
          </b-dropdown-item>
        </b-dropdown>
        <b-button v-b-modal.modalStyle>I Need Details</b-button>
      </div>

      <!--images-->
      <div class="text-left mt-3">
        <div v-if="images.length" class="pb-3">
          <hr>
        </div>
        <span v-for="img in images">
          <img :src="img" :style="{ width: img_size + 'px', height: img_size + 'px'}"/>
        </span>
      </div>
    </div>

    <!--Style Modal-->
    <b-modal id="modalStyle"
             title="Change How Things are Plotted"
             @ok="handleStyle">
      <b-form-group label="Dot Radius (in Pixels):"
                    description="Smaller number reveals finer cluster structure, but I'm trypophobia ...">
        <b-form-input type="number" v-model="point_size"></b-form-input>
      </b-form-group>
      <b-form-group label="Logo Image Size (in Pixels):"
                    description="Original image size is 64x64 pixels.">
        <b-form-input type="number" v-model="img_size"></b-form-input>
      </b-form-group>
    </b-modal>
  </div>
</template>

<script>
  import {draw, setData, setCb} from '../controllers/scatter_tsne'
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
  }

  /**
   * Based on the option, slice the data array differentially to be a subset.
   * @param points An array of points, passed by reference
   * @param option Slicing option
   */
  function sliceData (points, option) {
    if (option === 0) {
      setData(_.slice(points, TRAIN_SPLIT))
    } else if (option === 1) {
      setData(_.slice(points, 0, TRAIN_SPLIT))
    } else {
      setData(points)
    }
  }

  /**
   * Wrap the draw function
   * @param points
   */
  function lets_draw (points) {
    sliceData(points, this.data_slice)
    draw('#container', this.point_size)
  }

  export default {
    name: 'ScatterPage',
    data () {
      return {
        dim: 32,
        perplexity: 30,
        data_slice: 1,
        images: [],
        point_size: 4,
        img_size: 48,
        all_dims: [32, 64, 128, 256, 512, 1024],
        all_perplexity: [5, 10, 30, 50, 100],
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
      store.getTsnePoints(this.dim, this.perplexity)
        .then((points) => {
          lets_draw.call(this, points)
        }, (e) => {
          this.err = e
        })
    },
    methods: {
      handleStyle () {
        let key = `${this.dim}_${this.perplexity}`
        let points = store.tsne[key]
        clear.call(this)
        lets_draw.call(this, points)
      },
      changeDim (dim) {
        this.dim = dim

        clear.call(this)

        store.getTsnePoints(this.dim, this.perplexity)
          .then((points) => {
            lets_draw.call(this, points)
          }, (e) => {
            this.err = e
          })
      },
      changePerp (perp) {
        this.perplexity = perp

        clear.call(this)

        store.getTsnePoints(this.dim, this.perplexity)
          .then((points) => {
            lets_draw.call(this, points)
          }, (e) => {
            this.err = e
          })
      },
      changeData (str) {
        clear.call(this)

        let key = `${this.dim}_${this.perplexity}`
        let points = store.tsne[key]

        if (/test/i.test(str)) {
          this.data_slice = 0
        } else if (/train/i.test(str)) {
          this.data_slice = 1
        } else {
          this.data_slice = 2
        }

        lets_draw.call(this, points)
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
    fill-opacity: .4;
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
