<template>
<div class="mt-5 ml-3 mr-3 d-flex">
  <div v-for="dim in dims"
       class="bd-col text-center">
    <h5>Dimension: {{dim}}</h5>
    <div class="mt-3 mb-3 text-muted" v-if="ready">
      Validation Loss: {{metrics[dim]['validation_loss']}}
    </div>
    <router-link to="/analogy" tag="a" class="btn btn-primary mb-3">
      Enter
    </router-link>

    <div :id="`vis-container-${dim}`"></div>
  </div>
</div>
</template>

<script>
  import {store, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import * as d3 from 'd3'
  import * as scale from 'd3-scale-chromatic'
  import InitialAxes from '../controllers/analogy/initial_axes'

  export default {
    name: 'Initial',
    data () {
      return {
        dims: CONFIG.dims,
        ready: false,
        metrics: {}
      }
    },
    mounted () {
      store.comparePage()
        .then((all) => {
          let initial = _.map(all[0], (v) => {
            return {'type': v[0], 'dim': Number(v[1]), 'subtype': v[2], 'score': Number(v[3])}
          })

          // init data
          _.each(_.uniqBy(initial, 'dim'), (dim) => {
            this.metrics[dim.dim] = {}
          })

          // wrangle initial metrics
          _.each(initial, (p) => {
            if (_.find)
            this.metrics[p.dim][p.type] = p.score
          })

          // wrangle axes
          _.map(all[3], (d, i) => {
            let dim = this.dims[i]
            let res = []
            _.each(_.range(dim), (j) => {
              res.push({x0: d[0][j], x1: d[1][j], x2: d[2][j], x3: d[3][j]})
            })
            this.metrics[dim]['axes'] = res

            let chart = new InitialAxes()
            this.metrics[dim]['chart'] = chart
            chart.setData(res)
            chart.draw(`#vis-container-${dim}`)
          })

          this.ready = true
        }, () => {})
    },
    methods: {
    }
  }
</script>

<style scoped>
  .bd-col {
    font-size: 0.8em;
    width: 16.66%;
  }

  .bd-col a{
    border-radius: 2rem !important;
    min-width: 100px;
  }
</style>