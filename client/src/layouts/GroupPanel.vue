<template>
  <div v-if="shared.tab === 0">
    <!--Tabs-->
    <b-nav justified tabs class="ml-3 mr-3 mt-1 bd-panel-tab">
      <b-nav-item active>Groups</b-nav-item>
      <b-nav-item @click="clickTab">Vectors</b-nav-item>
    </b-nav>

    <!--Top Division-->
    <div class="d-flex bd-border-bottom" v-if="selected.length">
      <!--Back Button-->
      <div @click="removeAll" title="Clear your selection and start over"
           class="bd-btn-trans p-3" v-b-tooltip.hover>
        <i class="fa fa-fw fa-arrow-left text-muted"></i>
      </div>

      <!--Title-->
      <div class="p-3 w-100 text-center text-truncate">
        {{alias || 'Untitled Group'}}
      </div>

      <!--Right Buttons-->
      <div>
        <div title="Save your selection" class="bd-btn-trans p-3"
             v-b-tooltip.hover @click="load_only = false" v-b-modal.modal-save>
          <i class="fa fa-fw fa-cloud-upload text-muted"></i>
        </div>
      </div>
    </div>

    <!--Main View-->
    <div class="bd-group-panel-body" :class="{long: !selected.length}">
      <!--Search Bar-->
      <div class="p-3 bd-border-bottom" v-if="show_search">
        <auto-complete v-model="selection" :points="points" hint="Search ..."
                       v-on:chosen="addItem"
                       v-on:tentative="hoverItem"></auto-complete>
      </div>

      <!--Hints-->
      <div class="d-flex align-items-center m-3 h-100" v-if="!selected.length">
        <div class="text-center w-100 mb-3 text-muted">
          Start by brushing or searching!
        </div>
      </div>

      <!--Logo List-->
      <div class="ml-2 mr-2 mt-2" v-if="selected.length">
        <div class="d-flex justify-content-between text-muted mb-2">
          <div><small>{{selected.length}} total</small></div>
          <div v-if="cluster_score">
            <small title="Higher score indicates tighter cluster"
                   v-b-tooltip.hover >Cluster Score: {{cluster_score}}</small>
          </div>
        </div>
        <div class="d-flex flex-column-reverse">
          <div v-for="p in selected_points" :key="p.i"
               @click="clickLogo(p)"
               @mouseover="hoverLogo(p)"
               @mouseout="unhoverLogo">
            <list-row :p="p" hoverColor="#eee">
              <button class="close p-2 mr-2"
                      @mouseover.stop=""
                      @click.stop="removeItem(p)">
                <span>&times;</span>
              </button>
            </list-row>
          </div>
        </div>
      </div>

      <!--Show more-->
      <div class="p-2 text-center" v-if="selected.length > show_limit">
        <small class="text-muted">... and {{selected.length - selected_points.length}} more</small>
        <button @click="clickMore" class="btn btn-link btn-sm">
          show next 50</button>
      </div>
    </div>

    <!--Footer-->
    <div class="bd-panel-footer p-3">
      <div class="bd-panel-footer-margin" v-if="selected.length">
        <!--View Buttons-->
        <div class="btn-group btn-group-sm d-flex w-100">
          <b-btn class="btn btn-outline-secondary w-100"
                 v-b-tooltip.hover :title="`Display all points`"
                 :class="{active: view_mode === 1}"
                 @click="toggleAll">Show All</b-btn>
          <b-btn class="btn btn-outline-secondary w-100"
                 :class="{active: view_mode === 2}"
                 :disabled="view_mode === 3"
                 v-b-tooltip.hover :title="`Highlight the selected points`"
                 @click="toggleSubset">Highlight</b-btn>
          <b-btn class="btn btn-outline-secondary w-100"
                 v-b-tooltip.hover :title="`PCA over selected points`"
                 :class="{active: view_mode === 3}"
                 :disabled="!canPca()"
                 @click="reproject">Isolate</b-btn>
        </div>
      </div>

      <div class="bd-panel-footer-margin text-center" v-if="!selected.length">
        <b-btn class="btn-outline-warning mr-3"
               v-b-modal.modal-save @click="load_only=true">
          Load
        </b-btn>
        <b-btn class="btn-outline-warning"
               v-b-modal.modal-upload>
          Upload
        </b-btn>
      </div>
    </div>

    <!--Save and Load Modal-->
    <group-save-modal v-on:load="load" :load_only="load_only"></group-save-modal>

    <!--Upload Modal-->
    <group-upload-modal></group-upload-modal>
  </div>

</template>

<script>
  import AutoComplete from './AutoComplete.vue'
  import GroupSaveModal from './GroupSaveModal.vue'
  import {store, bus, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import ListRow from './ListRow.vue'
  import GroupUploadModal from './GroupUploadModal.vue'

  const BULK = 50

  export default {
    name: 'SearchPanel',
    props: {
      // Note that these points only contain index and meta information.
      points: {
        type: Array,
        required: true
      },
      latent_dim: {
        type: Number,
        required: true
      },
      view_state: {
        type: Number,
        required: true
      }
    },
    components: {
      GroupUploadModal,
      ListRow,
      AutoComplete,
      GroupSaveModal
    },
    data () {
      return {
        selection: '',
        selected: store.selected,
        shared: store.state,
        show_search: CONFIG.search.simple,
        show_limit: BULK,
        cluster_score: null,
        load_only: false,
        alias: null,
        view_mode: 1 // 1 - All, 2 - Highlight, 3 - Reprojected
      }
    },
    watch: {
      view_state () {
        if (this.view_state !== 1) {
          this.view_mode = 1
        }
      },
      selected () {
        this.clusterScore()
      },
      latent_dim () {
        this.clusterScore()
      }
    },
    computed: {
      selected_points: function () {
        return _.map(_.slice(this.selected, 0, this.show_limit), (i) => this.points[i])
      }
    },
    methods: {
      // button "show all"
      toggleAll () {
        if (this.view_mode === 2) {
          bus.$emit('highlight-subset', null)
        } else if (this.view_mode === 3) {
          this.$emit('original')
        }
        this.view_mode = 1
      },

      // button "highlight"
      toggleSubset () {
        if (this.view_mode === 3) return
        this.view_mode = 2
        bus.$emit('highlight-subset', store.selected)
      },

      // button "isolate"
      reproject () {
        this.view_mode = 3
        if (this.canPca()) {
          this.$emit('reproject', store.selected)
        }
      },

      clickMore () {
        this.show_limit = Math.min(this.show_limit + BULK, store.selected.length)
      },

      // load logo group
      load (group) {
        this.alias = group.alias
        while (store.selected.length) {
          store.selected.splice(0, 1)
        }

        _.each(group.list, (i) => {
          store.selected.push(i)
        })
      },

      // compute cluster score
      clusterScore () {
        const limit = 500

        this.cluster_score = null
        // for performance reason, do not compute if the group has too many items
        if (this.selected.length && this.selected.length < limit) {
          store.clusterScore(this.latent_dim, this.selected)
            .then((s) => {
              this.cluster_score = Math.round(s * 100) + '%'
            }, (e) => {
              alert(e) //TODO: handle error
            })
        }
      },

      // the tab at top
      clickTab () {
        store.state.tab = 1
      },

      // you need more than 3 points for PCA
      canPca () {
        return store.selected.length > 3
      },

      // modify the list
      addItem (p) {
        if (!_.includes(store.selected, p.i)) {
          store.selected.push(p.i)
        }
      },
      removeItem (p) {
        let idx = _.findIndex(store.selected, (i) => i === p.i)
        store.selected.splice(idx, 1)
      },
      removeAll () {
        this.alias = null
        this.show_limit = BULK
        while (store.selected.length) {
          store.selected.splice(0, 1)
        }

        // switch to default mode
        this.toggleAll()
      },
      hoverItem(p) {
        // 1. text data: highlight position in the plot
        if (CONFIG.data_type === 'text') {
          bus.$emit('highlight', null)
          if (p) {
            bus.$emit('highlight', p.i)
          }
        } else {
          // 2. other data: show meta
          if (p) {
            store.state.detail_card = p
          }
        }
      },

      // interactions of the logo list
      clickLogo (p) {
        // center the view around the point
        // this.$emit('center', p.i)
        store.state.detail_card = p
      },
      hoverLogo (p) {
        bus.$emit('highlight', p.i)
      },
      unhoverLogo () {
        bus.$emit('highlight', null)
      },

      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>

<style>
  .bd-group-panel-body {
    height: calc(100vh - 15rem);
    overflow-y: auto;
  }

  .bd-group-panel-body.long {
    height: calc(100vh - 11.45rem) !important;
  }

  .bd-panel-footer {
    box-shadow: 0.5rem 0 2rem rgba(0,0,0,.03);
    border-top: 1px solid rgba(0,0,0,.1);
  }

  .bd-panel-footer-margin {
    margin-bottom: 9px;
  }

  .bd-border-bottom {
    border-bottom: 1px solid rgba(0,0,0,.1);
  }

  .bd-panel-tab {
    min-height: 42px;
  }

  /*override*/
  .nav-item a {
    color: #6733cb;
  }
  .nav-item a:hover{
    color: #4b2e83;
  }
</style>
