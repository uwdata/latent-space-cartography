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
        {{focus.description || 'Untitled Vector'}}
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
      <!--Score-->
      <div>
        <div v-if="score" class="text-muted text-center m-3">
          <small v-b-tooltip.hover :title="score_hint">Angle Consistency: {{score}}</small>
        </div>
        <div v-if="!score" class="mb-3"></div>
      </div>

      <!--Start & End-->
      <div class="ml-3 mr-3 mb-3 d-flex bd-vector-groups">
        <!--Start Group-->
        <div class="bd-panel-card start bd-pointer w-50"
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

      <!--Vector Details Comparing Original & Analogy-->
      <div class="d-flex m-3" v-if="support_analogy && original && analogy">
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

      <!--List of the Most Different Output Dimensions-->
      <div class="m-3" v-if="data_type === 'other' && top">
        <list-top-signal :signals="top[1]" :start="false"
                         :name_start="focus.alias_start"
                         :name_end="focus.alias_end"></list-top-signal>
        <list-top-signal :signals="top[0]" :start="true" class="mt-3"
                         :name_start="focus.alias_start"
                         :name_end="focus.alias_end"></list-top-signal>
      </div>
    </div>

    <!--Footer-->
    <div class="bd-panel-footer" v-if="detail && support_analogy">
      <!--Apply Analogy-->
      <div class="d-flex justify-content-center" v-if="!loading_analogy">
        <div class="mt-3">
          <button class="btn btn-light" @click="applyAnalogy()">Apply Analogy</button>
          <img :src="imageUrl(detail.i)" class="bd-footer-img" />
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
  </div>
</template>

<script>
  import {store, bus, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import VueLoading from 'vue-loading-template'
  import ListTopSignal from './ListTopSignal.vue'
  import * as d3 from 'd3'

  export default {
    name: 'VectorFocusView',
    components: {
      ListTopSignal,
      VueLoading},
    props: {
      latent_dim: {
        type: Number,
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
        support_analogy: CONFIG.data_type === 'image',
        data_type: CONFIG.data_type,
        totalImage: 5,
        score: null,
        score_hint: 'The average cosine similarity between all possible start and end pairs',
        analogy: null,
        original: null,
        top: null,
        flipped: false,
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
      store.vectorScore(this.latent_dim, this.focus.start, this.focus.end)
        .then((s) => {
          this.score = Math.round(s * 100) + '%'
        }, (e) => {
          alert(e)
        })
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
        this.chart._vectors.clearData()
        this.$emit('back')
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
        let data = _.concat(top[0], top[1])
        let xMax = d3.max(data, (d) => Math.abs(d.diff)) * 1.05
        let xMin = d3.min(data, (d) => Math.abs(d.diff)) * 1.05
        let scale = d3.scaleLinear().range([0, 100]).domain([xMin, xMax])
        top[0] = _.map(top[0], (t) => _.extend({}, t, {width: scale(Math.abs(t.diff))}))
        top[1] = _.reverse(_.map(top[1], (t) => _.extend({}, t, {width: scale(Math.abs(t.diff))})))
        this.top = top
      },

      applyAnalogy (flipped = false) {
        this.loading_analogy = true

        let start = flipped ? this.focus.end : this.focus.start
        let end = flipped ? this.focus.start : this.focus.end

        store.applyAnalogy(this.latent_dim, this.detail.i, start, end)
          .then((line) => {
            this.loading_analogy = false
            this.flipped = flipped
            this.analogy = line
            this.chart._vectors.analogy = line
            this.chart._vectors.redraw()
          }, (e) => {
            this.loading_analogy = false
            alert(e)
          })
      },

      // helper
      imageUrl (i) {
        return store.getImageUrl(i)
      }
    }
  }
</script>

<style>
  .bd-btn-trans {
    display: inline-block;
    cursor: pointer;
  }
  .bd-btn-trans:hover {
    background-color: #eee;
  }

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
