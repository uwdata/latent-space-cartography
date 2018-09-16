<template>
  <div>
    <!--Top Division-->
    <div class="d-flex bd-border-bottom">
      <!--Back Button-->
      <div @click="clickBack" title="Back to Vector List"
           class="bd-btn-trans p-3" v-b-tooltip.hover>
        <i class="fa fa-fw fa-arrow-left text-muted"></i>
      </div>

      <!--Title-->
      <div class="p-3 w-100 text-center text-truncate">
        {{focus.description || `${focus.alias_end} - ${focus.alias_start}`}}
      </div>

      <!--Right Buttons-->
      <div>
        <div title="Delete Vector" class="bd-btn-trans p-3"
             v-b-tooltip.hover @click="clickDelete">
          <i class="fa fa-fw fa-trash-o text-muted"></i>
        </div>
      </div>
    </div>

    <!--Main View-->
    <div class="bd-focus-panel-body">
      <!--Start & End-->
      <div class="m-3 d-flex bd-vector-groups">
        <!--Start Group-->
        <div class="bd-panel-card start bd-pointer w-50"
             @mouseover="hoverGroup(focus.list_start)"
             @mouseout="hoverGroup()"
             @click="viewGroup(focus.list_start)">

          <!--If we have images-->
          <div v-if="data_type === 'image'">
            <div>
              <b>Start:</b>
              <div class="text-truncate">{{focus.alias_start}}</div>
            </div>
            <div class="mt-2">
              <img v-for="pi in focus.list_start.slice(0, totalImage)"
                   :src="imageUrl(pi)" class="bd-img-box"/>
              <div class="text-right">
                <small class="text-muted" v-if="startMore">
                  ... {{startMore}} more
                </small>
              </div>
            </div>
          </div>

          <!--If we don't have images-->
          <div v-else>
            <b>Start:</b>
            <div class="mb-2">{{focus.alias_start}}</div>
            <small class="text-muted">{{focus.list_start.length}} total</small>
          </div>
        </div>

        <!--End Group-->
        <div class="bd-panel-card end bd-pointer ml-3 w-50"
             @mouseover="hoverGroup(focus.list_end)"
             @mouseout="hoverGroup()"
             @click="viewGroup(focus.list_end)">

          <!--If we have images-->
          <div v-if="data_type === 'image'">
            <div>
              <b>End:</b>
              <div class="text-truncate">{{focus.alias_end}}</div>
            </div>
            <div class="mt-2">
              <img v-for="pi in focus.list_end.slice(0, totalImage)"
                   :src="imageUrl(pi)" class="bd-img-box"/>
              <div class="text-right">
                <small class="text-muted" v-if="endMore">
                  ... {{endMore}} more
                </small>
              </div>
            </div>
          </div>

          <!--If we don't have images-->
          <div v-else>
            <b>End:</b>
            <div class="mb-2">{{focus.alias_end}}</div>
            <small class="text-muted">{{focus.list_end.length}} total</small>
          </div>
        </div>
      </div>

      <!--Tutorial-->
      <div class="m-3" v-if="need_help && tutorial.vector">
        <div class="bd-panel-card">
          <div class="mb-2 text-center"><b>Pro Tips</b></div>
          <div style="font-size: 0.85rem">
            <div>
              The vector lives in the multi-dimensional latent space.
              It travels between the centroid of the start and end group,
              walking in constant steps to generate those images.
            </div>
            <div class="mt-3">
              To project to 2D, the X axis follows the vector direction,
              and the Y axis is the orthogonal 1st Principal Component.
            </div>
          </div>
          <div class="mt-3 text-right">
            <button class="btn btn-link btn-sm"
                    @click="tutorial.vector=false">Don't show again</button>
            <button class="btn btn-info btn-sm ml-2"
                    @click="need_help=false">Gotcha</button>
          </div>
        </div>
      </div>

      <!--Hint-->
      <div v-if="!detail && support_analogy" class="m-5 text-muted text-center">
        Select a point (click, or search) to apply this attribute vector.
      </div>


      <!--Pairs-->
      <div class="m-3">
        <!--Title-->
        <div class="bd-subtitle mb-1 text-uppercase">
          Pairs within the vector
          <!--Toggle button-->
          <span class="ml-2 pl-2 pr-2 bd-btn-trans" @click.stop="togglePairs"
                v-b-tooltip.hover :title="show_pairs ? 'Hide Pairs' : 'Show Pairs'">
            <i class="fa" :class="{'fa-eye-slash': !show_pairs, 'fa-eye': show_pairs}"></i>
          </span>
        </div>

        <!--Histogram-->
        <div id="hist-container"></div>
        <div v-if="score" class="text-center" style="font-size: 10px;">
          Pairwise Cosine Similarity</div>
      </div>

      <!--Vector Details Comparing Original & Analogy-->
      <div class="d-flex m-3" v-if="data_type === 'image' && original && analogy">
        <!--Original-->
        <div class="w-50 d-flex mt-3"
             :class="{'flex-column-reverse': flipped, 'flex-column': !flipped}">
          <p class="text-right" v-if="!flipped"><b>Original</b></p>
          <div v-for="d in original" class="div-48 text-right">
            <span class="text-muted mr-2">{{d.neighbors}}</span>
            <img :src="imageUrl(d.nearest)" class="img-24 mr-2"/>
            <img :src="`/build/${d.image}`" class="img-48"/>
          </div>

          <!--when flipped, everything is in reverse-->
          <div class="div-48" v-if="flipped"><div class="img-48"></div></div>
          <p class="text-right" v-if="flipped"><b>Original</b></p>
        </div>
        <!--Analogy-->
        <div class="w-50 d-flex flex-column mt-3 ml-3">
          <p><b>Analogy</b></p>
          <div v-for="d in analogy" class="div-48">
            <img :src="`/build/${d.image}?${flipped}`" class="img-48"/>
            <img :src="imageUrl(d.nearest)" class="img-24 ml-2"/>
            <span class="text-muted ml-2">{{d.neighbors}}</span>
          </div>
        </div>
      </div>

      <!--List of Nearest Neighbors-->
      <div class="m-3" v-if="data_type === 'text' && answer">
        <div class="bd-subtitle text-uppercase mb-2">Nearest Neighbors of Analogy</div>
        <div class="d-flex">
          <div class="w-50">
            <div class="mb-2 bd-subtitle text-center">Original</div>
            <list-knn :list="answer_comp" :compact="true"></list-knn>
          </div>
          <div class="w-50">
            <div class="mb-2 bd-subtitle text-center">Answer</div>
            <list-knn :list="answer" :compact="true"></list-knn>
          </div>
        </div>
      </div>

      <!--List of the Most Different Output Dimensions-->
      <div class="m-3" v-if="data_type === 'other' && top">
        <list-top-signal :signals="top[1]" :start="false"
                         :name_start="focus.alias_start"
                         :name_end="focus.alias_end"></list-top-signal>
        <list-top-signal :signals="top[0]" :start="true" class="mt-3"
                         :name_start="focus.alias_start"
                         :name_end="focus.alias_end"></list-top-signal>
      </div>

      <!--Other vectors-->
      <div class="m-3" v-if="vecs.length">
        <!--Title-->
        <div class="bd-subtitle mb-2 text-uppercase">
          Other Vectors
          <!--Toggle button-->
          <span class="ml-2 pl-2 pr-2 bd-btn-trans" @click.stop="toggleVectorPlot"
                v-b-tooltip.hover :title="other_vec ? 'Hide Vectors' : 'Visualize Vectors'">
            <i class="fa" :class="{'fa-eye-slash': !other_vec, 'fa-eye': other_vec}"></i>
          </span>
        </div>

        <!--List-->
        <div class="d-flex mb-1 text-muted bd-vec-table-header">
          <div class="w-25 text-right mr-2 text-uppercase">Cosine</div>
          <div class="w-75 text-uppercase">Label</div>
        </div>
        <div v-for="v in vecs" style="font-size: 0.7em;" class="d-flex">
          <div class="w-25 text-right mr-2">{{v.cosine}}</div>
          <div class="w-75 text-truncate">{{v.label}}</div>
        </div>
      </div>
    </div>

    <!--Footer-->
    <div class="bd-panel-footer" v-if="detail && support_analogy">
      <!--Apply Analogy-->
      <div class="d-flex justify-content-center" v-if="!loading_analogy">
        <div class="mt-3">
          <button class="btn btn-light" @click="applyAnalogy()">Apply Analogy</button>
          <img v-if="data_type === 'image'" :src="imageUrl(detail.i)"
               class="bd-footer-img" />
          <span class="text-center text-truncate bd-footer-img"
               v-if="data_type === 'text'">{{detail.name}}</span>
          <button class="btn btn-light" @click="applyAnalogy(true)">Reverse Analogy</button>
        </div>
      </div>

      <!--Loading-->
      <div v-if="loading_analogy"
           class="d-flex justify-content-center mt-3">
        <vue-loading type="bars" color="#4b2e83"
                     :size="{ width: '2rem', height: '1rem' }"></vue-loading>
      </div>
    </div>

    <!--Footer for gene data-->
    <div class="bd-panel-footer" v-if="data_type === 'other'">
      <div class="text-center mt-3">
        <a class="btn btn-light" @click="saveFile">Export Gene List</a>
      </div>
    </div>
  </div>
</template>

<script>
  import {store, bus, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import VueLoading from 'vue-loading-template'
  import ListTopSignal from './ListTopSignal.vue'
  import * as d3 from 'd3'
  import { saveAs } from 'file-saver/FileSaver'
  import ListKnn from './ListKnn.vue'
  import Histogram from '../controllers/analogy/histogram'

  export default {
    name: 'VectorFocusView',
    components: {
      ListKnn,
      ListTopSignal,
      VueLoading
    },
    props: {
      latent_dim: {
        type: Number,
        required: true
      },
      vectors: {
        required: true
      },
      focus: {
        required: true
      },
      chart: {
        required: true
      }
    },
    data () {
      return {
        shared: store.state,
        tutorial: store.tutorial,
        need_help: true,
        support_analogy: CONFIG.data_type === 'image'
          || CONFIG.data_type === 'text',
        data_type: CONFIG.data_type,
        totalImage: 5,
        vecs: [],
        chart_hist: new Histogram(),
        score: null,
        score_hint: 'The average cosine similarity between all possible start and end pairs',
        analogy: null,
        original: null,
        top: null,
        answer: null,
        answer_comp: null,
        flipped: false,
        other_vec: false,
        show_pairs: true,
        loading_analogy: false
      }
    },
    mounted () {
      this.need_help = true

      // register event
      bus.$on('draw-focus-vec', this.drawPrimaryVector)

      // vector style
      this.chart._vectors.data_type = CONFIG.data_type

      // vector score
      // for performance reason, skip if either group has too many items
      const limit = 500
      if (this.focus.list_start.length < limit && this.focus.list_end.length < limit) {
        store.vectorScore(this.latent_dim, this.focus.start, this.focus.end, true)
          .then((all) => {
            console.log(all)
            let mean = all[0]
            this.score = mean.toFixed(2)
            this.chart_hist.setData(all[1], all[2], mean)
            this.chart_hist.draw('#hist-container')
          }, (e) => {
            alert(e)
          })
      }

      // cosines to other vectors
      store.vectorDiff(this.latent_dim, this.focus.id)
        .then((cos) => {
          let vs = this.vectors
          _.each(cos, (c) => {
            let i = _.findIndex(vs, (v) => v.id === c.id)
            this.vecs.push({
              cosine: Number(c.cosine).toFixed(2),
              label: `${vs[i].alias_end} - ${vs[i].alias_start}`})
          })
        }, (e) => {
          alert(e)
        })
    },
    beforeDestroy () {
      if (this.chart._pairs) {
        this.chart._pairs.hide = false
        this.chart._pairs.setData([])
        this.chart._pairs.redraw()
      }
      if (this.chart._vectors) {
        this.chart._vectors.clearData()
        this.chart._vectors.redraw()
      }

      // unregister event
      bus.$off('draw-focus-vec', this.drawPrimaryVector)
    },
    computed: {
      startMore: function () {
        return Math.max(0, this.focus.list_start.length - this.totalImage)
      },
      endMore: function () {
        return Math.max(0, this.focus.list_end.length - this.totalImage)
      },
      detail () {
        return this.shared.clicked_point
      }
    },
    methods: {
      // go back to the list
      clickBack () {
        if (this.other_vec) {
          this.toggleVectorPlot() // turn off
        }

        this.$emit('back', true)
      },

      // delete this vector
      // TODO: ask user to confirm
      clickDelete () {
        store.deleteVector(this.focus.id)
          .then(() => {
            this.clickBack()
          }, (e) => {
            alert(e)
          })
      },

      togglePairs () {
        this.show_pairs = !this.show_pairs
        this.chart._pairs.hide = !this.show_pairs
        this.chart._pairs.redraw()
      },

      // toggle the visibility of vectors plotted on the global view
      toggleVectorPlot () {
        this.other_vec = !this.other_vec
        this.chart._global_vectors.hide = !this.other_vec
        this.chart._global_vectors.redraw()
      },

      // hover to highlight a group
      hoverGroup (indices) {
        bus.$emit('highlight-subset', indices)
      },

      viewGroup (list) {
        while (store.selected.length) {
          store.selected.splice(0, 1)
        }

        _.each(list, (i) => {
          store.selected.push(i)
        })

        store.state.tab = 0
      },

      drawPrimaryVector (vector, top) {
        this.original = vector.line

        this.chart._vectors.primary = vector
        this.chart._vectors.redraw()

        // the strongest output signal (for arbitrary tensor data type)
        if (CONFIG.data_type === 'other') {
          let data = _.concat(top[0], top[1])
          let xMax = d3.max(data, (d) => Math.abs(d.diff)) * 1.05
          let xMin = d3.min(data, (d) => Math.abs(d.diff)) * 1.05
          let scale = d3.scaleLinear().range([0, 100]).domain([xMin, xMax])
          top[0] = _.map(top[0], (t) => _.extend({}, t, {width: scale(Math.abs(t.diff))}))
          top[1] = _.map(top[1], (t) => _.extend({}, t, {width: scale(Math.abs(t.diff))}))
          this.top = top
        }

        // ask someone else to draw the individual pairs
        bus.$emit('draw-pairs')
      },

      applyAnalogy (flipped = false) {
        this.loading_analogy = true

        let start = flipped ? this.focus.end : this.focus.start
        let end = flipped ? this.focus.start : this.focus.end
        let answer = []

        store.applyAnalogy(this.latent_dim, this.detail.i, start, end)
          .then((all) => {
            let line = all[0]
            answer = all[1]

            this.loading_analogy = false
            this.flipped = flipped
            this.analogy = line
            this.chart._vectors.analogy = line
            this.chart._vectors.redraw()

            return store.getKnn(this.latent_dim, this.detail.i)
          }, (e) => {
            this.loading_analogy = false
            alert(e)
          })
          .then((words) => {
            let same = _.keyBy(_.intersectionBy(answer, words, 'name'), 'name')
            this.answer = _.map(answer, (w) => _.extend({}, w, {muted: w.name in same}))
            this.answer_comp = _.map(words, (w) => _.extend({}, w, {muted: w.name in same}))
          }, () => {})
      },

      // save gene list as an CSV file
      saveFile () {
        let rows = [['gene', 'difference']]
        _.each(this.top, (t) => {
          _.each(t, (d) => {
            rows.push([d.gene, d.diff])
          })
        })

        let content = ''
        _.each(rows, (row) => {
          content += row.join(',') + '\r\n'
        })

        let blob = new Blob([content], {type: 'data:text/csv;charset=utf-8'})
        saveAs(blob, `${this.focus.alias_end}-${this.focus.alias_start}.csv`)
      },

      // helper
      imageUrl (i) {
        return store.getImageUrl(i)
      }
    }
  }
</script>

<style>
  .bd-vector-groups {
    width: calc(25vw - 3rem);
  }

  .bd-panel-card {
    border: #ddd 1px solid;
    padding: 15px 15px 20px;
    background-color: #fff;
  }

  .bd-panel-card.start {
    border-top: rgba(131,88,213, 0.2) 6px solid;
  }

  .bd-panel-card.end {
    border-top: rgba(244,196,76, 0.2) 6px solid;
  }

  .bd-panel-card:hover {
    background-color: #fafafa;
  }

  .bd-img-box {
    width: 20%;
    height: 20%;
  }

  .bd-focus-panel-body {
    height: calc(100vh - 15rem);
    overflow-y: auto;
  }

  .bd-footer-img {
    width: 2.5rem;
    height: 2.5rem;
  }

  .img-24 {
    width: 24px;
    height: 24px;
  }

  .img-48 {
    width: 48px;
    height: 48px;
  }

  .div-48 {
    line-height: 48px;
    font-size: 0.7em;
  }

  .bd-vec-table-header {
    font-size: 0.7em;
    border-bottom: 1px solid #eee;
  }

  .btn-outline-theme {
    color: #4b2e83;
    background-color: transparent;
    border-color: #4b2e83;
  }

  .btn-outline-theme.active {
    color: #fff;
    background-color: #4b2e83;
  }
</style>
