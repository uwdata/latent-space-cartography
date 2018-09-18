<template>
<div class="d-flex justify-content-center">
  <!--Analogy-->
  <div class="mt-3 mr-5">
    <h5>Google's Analogy Test</h5>
    <table>
      <tr>
        <th>Category</th>
        <th v-for="dim in dims">{{dim}}D</th>
      </tr>
      <tr v-for="row in analogy">
        <td class="pr-3">{{row[0]}}</td>
        <td v-for="cell in row.slice(1)"
            :style="{background: getColor('analogy', cell)}"
            class="bd-num text-center">
          <div>{{cell}}</div>
        </td>
      </tr>
    </table>
  </div>

  <!--Vectors-->
  <div class="mt-3">
    <h5>Attribute Vector Consistency Score</h5>
    <table>
      <tr>
        <th>Attribute Vector</th>
        <th v-for="dim in dims">{{dim}}D</th>
      </tr>
      <tr v-for="row in vectors">
        <td class="pr-3">{{row[0]}}</td>
        <td v-for="cell in row.slice(1)"
            :style="{background: getColor('vectors', cell)}"
            class="bd-num text-center">{{cell.toFixed(2)}}</td>
      </tr>
    </table>
  </div>
</div>
</template>

<script>
  import {store, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import * as d3 from 'd3'
  import * as scale from 'd3-scale-chromatic'

  export default {
    name: 'ComparePage',
    data () {
      return {
        dims: CONFIG.dims,
        analogy: [],
        vectors: [],
        raw_analogy: [],
        raw_vectors: []
      }
    },
    mounted () {
      store.comparePage()
        .then((all) => {
          let initial = _.map(all[0], (v) => {
            return {'type': v[0], 'dim': Number(v[1]), 'subtype': v[2], 'score': Number(v[3])}
          })

          // wrangle analogy table
          let analogy = _.filter(initial, (r) => r.type === 'analogy')
          this.raw_analogy = analogy
          analogy = _.groupBy(analogy, 'subtype')
          analogy = _.map(analogy, (group) => {
            let res = [group[0].subtype]
            _.each(this.dims, (dim) => {
              res.push(_.find(group, {'dim': dim}).score)
            })
            return res
          })
          this.analogy = analogy

          // wrangle vector table
          let vectors = _.keyBy(all[2], 'id')
          let scores = _.map(all[1], (v) => {
            let vid = Number(v[1])
            return {
              'dim': Number(v[0]),
              'vid': vid,
              'name': store.getVectorName(vectors[vid]),
              'score': Number(v[2])
            }
          })
          this.raw_vectors = scores
          scores = _.groupBy(scores, 'name')
          this.vectors = _.map(scores, (group) => {
            let res = [group[0].name]
            _.each(this.dims, (dim) => {
              res.push(_.find(group, {'dim': dim}).score)
            })
            return res
          })
        }, () => {})
    },
    methods: {
      getColor (which, score) {
        let max = d3.max(this[`raw_${which}`], (d) => d.score)
        return scale.interpolateBlues(score / max)
      }
    }
  }
</script>

<style scoped>
  .bd-num {
    font-size: 0.8em;
    /*color: #99979c;*/
    color: white;
    min-width: 50px;
  }

  tr {
    height: 30px;
  }
</style>