<template>
  <div v-if="tab.index === 0">
    <!--Tabs-->
    <b-nav justified tabs class="ml-3 mr-3 mt-1">
      <b-nav-item active>Groups</b-nav-item>
      <b-nav-item @click="clickTab">Vectors</b-nav-item>
    </b-nav>

    <!--Top Division-->
    <div class="m-3">
      <auto-complete v-model="selection" :points="points" hint="Search a brand ..."
                     v-on:chosen="addItem"
                     v-on:tentative="hoverItem"></auto-complete>
    </div>
    <hr>

    <!--Hint-->
    <div v-if="!selected.length" class="m-5 d-flex align-items-center bd-logo-list">
      <div>
        <div class="text-muted text-center">
          Start by brushing the dots, or searching for a brand name!
        </div>
        <button class="w-100 mt-3 btn btn-warning" v-b-modal.modal-save>Load</button>
      </div>
    </div>

    <!--Logo List-->
    <div v-if="selected.length" class="m-3 bd-logo-list">
      <p>Selected logos:</p>
      <div v-for="p in selected_points" :key="p.i"
           @click="clickLogo(p)"
           @mouseover="hoverLogo(p)"
           @mouseout="unhoverLogo">
        <list-row :p="p" hoverColor="#eee">
          <button class="close p-2"
                  @mouseover.stop=""
                  @click.stop="removeItem(p)">
            <span>&times;</span>
          </button>
        </list-row>
      </div>
    </div>

    <!--Footer-->
    <div v-if="selected.length" class="bd-panel-footer p-3">
      <div class="d-flex justify-content-between">
        <!--View Buttons-->
        <div class="btn-group btn-group-sm d-flex w-100">
          <b-btn class="btn btn-outline-secondary w-100"
                 v-b-tooltip.hover :title="`Display all logos`"
                 :class="{active: view_mode === 1}"
                 @click="toggleAll">Show All</b-btn>
          <button class="btn btn-outline-secondary w-100"
                  :class="{active: view_mode === 2}"
                  v-b-tooltip.hover :title="`Display the selected logos`"
                  @click="toggleSubset">Highlight</button>
          <b-btn class="btn btn-outline-secondary w-100"
                 v-b-tooltip.hover :title="`PCA over selected logos`"
                 :class="{active: view_mode === 3}"
                 :disabled="!canPca()"
                 @click="reproject">Isolate</b-btn>
        </div>
        <div class="btn-group btn-group-sm ml-3">
          <b-btn class="btn btn-outline-secondary"
                 v-b-tooltip.hover :title="`Clear your selection`"
                 @click="removeAll">
            <i class="fa fa-fw fa-trash"></i>
          </b-btn>
          <b-btn class="btn btn-outline-secondary"
                 v-b-modal.modal-save
                 v-b-tooltip.hover :title="`Save your selection`">
            <i class="fa fa-fw fa-cloud-upload"></i>
          </b-btn>
        </div>
      </div>
    </div>

    <!--Save and Load Modal-->
    <group-save-modal v-on:load="load"></group-save-modal>
  </div>
</template>

<script>
  import AutoComplete from './AutoComplete.vue'
  import GroupSaveModal from './GroupSaveModal.vue'
  import {store} from '../controllers/config'
  import _ from 'lodash'
  import ListRow from './ListRow.vue'

  export default {
    name: 'SearchPanel',
    props: {
      // Note that these points only contain index and meta information.
      points: {
        type: Array,
        required: true
      }
    },
    components: {
      ListRow,
      AutoComplete,
      GroupSaveModal
    },
    data () {
      return {
        selection: '',
        selected: store.selected,
        tab: store.tab,
        view_mode: 1 // 1 - All, 2 - Subset, 3 - Reprojected
      }
    },
    computed: {
      selected_points: function () {
        return _.map(this.selected, (i) => this.points[i])
      }
    },
    methods: {
      // button "show all"
      toggleAll () {
        if (this.view_mode === 2) {
          this.$emit('subset', null)
        } else if (this.view_mode === 3) {
          this.$emit('original')
        }
        this.view_mode = 1
      },

      // button "highlight"
      toggleSubset () {
        if (this.view_mode === 3) return
        this.view_mode = 2
        this.$emit('subset', store.selected)
      },

      // button "re-project"
      reproject () {
        this.view_mode = 3
        if (this.canPca()) {
          this.$emit('reproject', store.selected)
        }
      },

      // load logo group
      load (group) {
        while (store.selected.length) {
          store.selected.splice(0, 1)
        }

        _.each(group.list, (i) => {
          store.selected.push(i)
        })
      },

      // the tab at top
      clickTab () {
        store.tab.index = 1
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
        while (store.selected.length) {
          store.selected.splice(0, 1)
        }

        // switch to default mode
        this.toggleAll()
      },
      hoverItem(p) {
        if (p) {
          store.state.detail_card = p
        }
      },

      // interactions of the logo list
      clickLogo (p) {
        // TODO: center view
      },
      hoverLogo (p) {
        store.state.detail_card = p
        this.$emit('highlight', p.i)
      },
      unhoverLogo () {
        this.$emit('highlight', null)
      },

      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>

<style>
  .bd-logo-list {
    overflow-y: auto;
    height: calc(100vh - 17.9rem);
  }

  .bd-panel-footer {
    box-shadow: 0.5rem 0 2rem rgba(0,0,0,.03);
    border-top: 1px solid rgba(0,0,0,.1);
  }
</style>
