<template>
  <div :class="{'d-none': shared.tab !== 1}">
    <!--Tabs-->
    <b-nav justified tabs class="ml-3 mr-3 mt-1">
      <b-nav-item @click="clickTab">Groups</b-nav-item>
      <b-nav-item active>Vectors</b-nav-item>
    </b-nav>

    <!--List View-->
    <div v-if="!focus">
      <!--Top Division-->
      <div class="m-3 bd-subtitle text-uppercase">
        Add Vector
      </div>
      <div class="m-3 d-flex">
        <!--Start-->
        <div class="d-inline-block" @click="which = 'start'"
             title="Choose a starting group"
             v-b-modal.modal-group v-b-tooltip.hover>
          <button v-if="!start" class="btn btn-outline-secondary">
            <i class="fa fa-fw fa-circle-o"></i>
          </button>
          <button v-if="start && !show_image" class="btn btn-info">
            <i class="fa fa-fw fa-check"></i>
          </button>
          <group-thumb v-if="start && show_image" :list="start.list" :width="4"
                       class="m-1 bd-pointer"></group-thumb>
        </div>

        <!--Middle-->
        <div class="d-inline-block w-100">
          <div class="bd-arrow h-50"></div>
          <button class="btn btn-sm bd-arrow-btn"
                  :class="{'btn-secondary': !start || !end, 'btn-warning': start && end}"
                  @click="clickAdd" :disabled="!start || !end">Add</button>
        </div>

        <!--End-->
        <div class="d-inline-block" @click="which = 'end'"
             title="Choose an ending group"
             v-b-modal.modal-group v-b-tooltip.hover>
          <group-thumb v-if="end" :list="end.list" :width="4"
                       class="m-1 bd-pointer"></group-thumb>
          <button v-if="end && !show_image" class="btn btn-info">
            <i class="fa fa-fw fa-check"></i>
          </button>
          <button v-if="!end" class="btn btn-outline-secondary">
            <i class="fa fa-fw fa-circle-o"></i>
          </button>
        </div>
      </div>

      <!--Vector List-->
      <div class="bd-vector-list p-3 pt-4" v-if="vectors.length">
        <div class="mb-3">
          <!--Title-->
          <div class="bd-subtitle text-uppercase">
            Vector List

            <!--Toggle button-->
            <span class="ml-2 pl-2 pr-2 bd-btn-trans" @click.stop="toggleVectorPlot"
                  v-b-tooltip.hover :title="plotted ? 'Hide Vectors' : 'Visualize Vectors'">
              <i class="fa" :class="{'fa-eye-slash': !plotted, 'fa-eye': plotted}"></i>
            </span>
          </div>
        </div>

        <!--Loading-->
        <div class="h-100 d-flex flex-column justify-content-center"
             v-if="loading_vectors">
          <div>
            <vue-loading type="spiningDubbles" color="#6c757d"
                         :size="{ width: '3rem', height: '3rem' }"></vue-loading>
            <div class="mt-4 text-center text-muted">Loading Vectors</div>
          </div>
        </div>

        <!--List of Vectors-->
        <div v-if="!loading_vectors" v-for="v in vectors"
             class="d-flex bd-vector"  @click="focusVector(v)"
             @mouseover="hoverVector(v)" @mouseout="hoverVector()">
          <div class="mr-2 d-flex flex-column">
            <i class="fa fa-fw fa-circle-o bd-arrow-end mt-1"></i>
            <div class="bd-arrow-vertical h-100"></div>
            <i class="fa fa-fw fa-circle-o bd-arrow-end"></i>
          </div>
          <div class="w-100">
            <div>
              <group-thumb :list="v.list_start" :width="4" :height="1"></group-thumb>
              <span class="ml-2 text-truncate">{{v.alias_start}}</span>
            </div>
            <div>
              <group-thumb :list="v.list_end" :width="4" :height="1"></group-thumb>
              <span class="ml-2 text-truncate">{{v.alias_end}}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!--Focus View-->
    <vector-focus v-if="focus" :focus="focus" :chart="chart" :vectors="vectors"
                  :latent_dim="latent_dim" v-on:back="unfocus"></vector-focus>

    <!--Modal-->
    <group-modal v-on:clickGroup="clickGroup"></group-modal>
  </div>
</template>

<script>
  import {store, CONFIG, bus} from '../controllers/config'
  import moment from 'moment'
  import GroupModal from './GroupModal.vue'
  import GroupThumb from './GroupThumbnail.vue'
  import VectorFocus from './VectorFocusView.vue'
  import VueLoading from 'vue-loading-template'
  import _ from 'lodash'

  export default {
    name: 'VectorPanel',
    props: {
      latent_dim: {
        type: Number,
        required: true
      },
      chart: {
        required: true
      },
      view_state: {
        type: Number,
        required: true
      },
      proj_state: {
        type: String,
        required: true
      }
    },
    components: {
      VueLoading,
      GroupModal,
      GroupThumb,
      VectorFocus
    },
    data () {
      return {
        start: null,
        end: null,
        which: 'start',
        // each vector contains: id, description, timestamp
        // start, list_start, alias_start, (and same for end)
        // path -- to visualize a vector in a global projection
        vectors: [],
        focus: null,
        plotted: false,
        shared: store.state,
        show_image: CONFIG.data_type === 'image',
        loading_vectors: false
      }
    },
    watch: {
      // when projection changes, get out of the vector view
      view_state () {
        if (this.view_state !== 2) {
          this.focus = null
        }
      },
      proj_state (val) {
        // custom projection rely on an async projection matrix
        if (/^tsne|^pca/.test(val)) {
          this.plotVectors()
        }
      }
    },
    mounted: function () {
      // register event
      bus.$on('draw-focus-vec', this.plotVectors)

      this.fetchVectors()
        .then(() => {
          // register callback
          // plotting has to be after fetching
          bus.$on('chart-ready', this.plotVectors)
        })
    },
    methods: {
      fetchVectors () {
        this.loading_vectors = true
        return store.getVectors()
          .then((vectors) => {
            this.loading_vectors = false
            this.vectors = vectors
          }, (e) => {
            this.loading_vectors = false
            alert(e)
          })
      },

      plotVectors () {
        if (!this.vectors.length) return

        let re = /^tsne|^pca|^vector$/i
        let supported = re.test(this.proj_state)
        if (!supported) {
          // clear previous plot
          this.chart._global_vectors.setData([])
          this.chart._global_vectors.redraw()
          return
        }

        let vs = _.map(this.vectors, (v) => [v.start, v.end])
        store.plotVectors(this.latent_dim, this.proj_state, vs)
          .then((data) => {
            // save the data
            data = _.map(data, (arr, i) => {
              let vt = this.vectors[i]
              return {
                id: 'glo-vec-' + i,
                label: `${vt.alias_start}-${vt.alias_end}`,
                coordinates: arr
              }
            })
            _.each(data, (path, i) => {
              this.vectors[i].path = path
            })

            // plot
            this.chart._global_vectors.setData(data)
            this.chart._global_vectors.redraw()
          }, (e) => {
            alert(e)
          })
      },

      // when a vector is hovered in the list
      hoverVector (v) {
        let vid = v ? (v.path ? v.path.id : null) : null
        this.chart._global_vectors.hoverVector(vid)
      },

      // toggle the visibility of vectors plotted on the global view
      toggleVectorPlot () {
        this.plotted = !this.plotted
        this.chart._global_vectors.hide = !this.plotted
        this.chart._global_vectors.redraw()
      },

      // the tab at top
      clickTab () {
        store.state.tab = 0
      },
      // when a group is selected
      clickGroup (group) {
        this[this.which] = group
      },
      // when the button "Add" is clicked
      clickAdd () {
        if (!this.start || !this.end) {
          return
        }

        store.createVector(this.start.id, this.end.id)
          .then(() => {
            this.start = null
            this.end = null
            this.fetchVectors() // TODO: only query for a single vector
          }, (e) => {
            alert(e)
          })
      },
      focusVector (vector) {
        if (this.plotted) {
          this.toggleVectorPlot() // turn off
        }
        this.focus = vector
        this.$emit('focus', vector)
      },
      unfocus (reload) {
        this.focus = null
        if (reload) {
          this.fetchVectors()
        }
        this.$emit('reset')
      },
      formatTime (t) {
        return moment(t).fromNow()
      }
    }
  }
</script>

<style>
  .bd-vector {
    border-left: #ddd 1px solid;
    border-right: #ddd 1px solid;
    border-top: #ddd 1px solid;
    padding: 15px;
    background-color: #fff;
    cursor: pointer;
  }
  .bd-vector:last-child {
    border-bottom: #ddd 1px solid;
  }
  .bd-vector:hover {
    background-color: #fafafa;
  }

  .bd-vector-list {
    overflow-y: auto;
    height: calc(100vh - 13rem);
  }

  .bd-arrow {
    border-bottom: 1px dotted #6c757d;
    margin-left: 15px;
    margin-right: 15px;
  }

  .bd-arrow-vertical {
    border-right: 2px dotted #6c757d;
    width: calc(50% + 1px);
  }

  .bd-arrow-end {
    color: #8c959d;
    font-size: 0.9em;
  }

  .bd-arrow-btn {
    position: absolute;
    left: 40%;
    margin-top: -15px;
  }
</style>
