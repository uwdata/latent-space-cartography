<template>
  <div class="row mt-5">
    <div class="col-2"></div>
    <div class="col-8 text-center">
      <h3 class="mb-3">Some Title.</h3>
      This is a description.
      <div id="container" class="mt-3"></div>
    </div>
    <div class="col-2"></div>
  </div>
</template>

<script>
  import {draw, setData} from '../controllers/scatter'
  import {store, log_debug} from '../controllers/config'
  import _ from 'lodash'

  export default {
    name: 'ScatterPage',
    data () {
      return {
        dim: 32,
        err: ''
      }
    },
    mounted: function () {
      store.getPoints(this.dim)
        .then((points) => {
          log_debug(points)
          setData(_.slice(points, 15000))
          draw('#container')
        }, (e) => {
          this.err = e
        })
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
