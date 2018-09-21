<template>
<div class="row">
  <div class="col-3 pr-0">
    <div style="margin-top: calc(9rem + 1px);">
      <div v-for="v in vectors" class="d-flex flex-row-reverse bd-vector">
        <div class="ml-2 d-flex flex-column">
          <i class="fa fa-fw fa-circle-o bd-arrow-end mt-1"></i>
          <div class="bd-arrow-vertical h-100"></div>
          <i class="fa fa-fw fa-circle-o bd-arrow-end"></i>
        </div>
        <div class="w-100 text-right">
          <div>
            <span class="ml-2 text-truncate">{{v.alias_start}}</span>
            <group-thumb :list="v.list_start" :width="4" :height="1"></group-thumb>
          </div>
          <div>
            <span class="ml-2 text-truncate">{{v.alias_end}}</span>
            <group-thumb :list="v.list_end" :width="4" :height="1"></group-thumb>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="col-9 pl-0 mt-3 d-flex">
    <div v-for="dim in dims"
         class="bd-col text-center">
      <h5>Dimension: {{dim}}</h5>
      <div class="mt-3 mb-3 text-muted" v-if="ready">
        Validation Loss: {{metrics[dim]['validation_loss']}}
      </div>
      <router-link to="/analogy" tag="a" class="btn btn-outline-primary mb-3">
        Enter
      </router-link>

      <!--vector scores-->
      <div>
        <div v-for="v in vectors" class="bd-vec-row">
          <div class="bd-dot"
               :style="{backgroundColor: getColor(metrics[dim].vectors[v.id]),
               color: getTextColor(metrics[dim].vectors[v.id])}">
            {{metrics[dim].vectors[v.id]}}</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
  import {store, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import GroupThumb from '../layouts/GroupThumbnail.vue'
  import * as d3 from 'd3'
  import * as scale from 'd3-scale-chromatic'

  export default {
    name: 'ComparePage',
    components: {GroupThumb},
    data () {
      return {
        dims: CONFIG.dims,
        ready: false,
        vectors: [],
        metrics: {},
        max_vector_score: 10
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
            this.metrics[dim.dim] = {vectors: {}}
          })

          // wrangle initial metrics
          _.each(initial, (p) => {
            if (_.find)
              this.metrics[p.dim][p.type] = p.score
          })

          // wrangle vectors
          this.vectors = all[2]
          _.each(all[1], (v) => {
            let vid = Number(v[1])
            let dim = Number(v[0])
            this.metrics[dim].vectors[vid] = Number(Number(v[2]).toFixed(2))
          })
          this.max_vector_score = d3.max(all[1], (d) => d[2])

          this.ready = true
        }, () => {})
    },
    methods: {
      getColor (score) {
        return scale.interpolateBlues(score / this.max_vector_score)
      },
      getTextColor (score) {
        let ratio = score / this.max_vector_score
        return ratio > 0.3 ? '#fff' : '#6c757d'
      }
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

  .bd-vec-row {
    border-top: #ddd 1px solid;
    height: 5rem;
  }

  .bd-dot {
    display: inline-block;
    border-radius: 50%;
    height: 3rem;
    width: 3rem;
    line-height: 3rem;
    margin-top:1rem;
  }

  /*related to vector list*/
  .bd-vector {
    border-top: #ddd 1px solid;
    padding: 15px 0 15px 15px;
    cursor: pointer;
    height: 5rem;
  }
  .bd-vector:hover {
    background-color: #fafafa;
  }
  .bd-arrow-vertical {
    border-right: 2px dotted #6c757d;
    width: calc(50% + 1px);
  }

  .bd-arrow-end {
    color: #8c959d;
    font-size: 0.9em;
  }
</style>