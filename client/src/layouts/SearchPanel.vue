<template>
  <div>
    <!--Top Division-->
    <div class="m-3">
      <auto-complete v-model="selection" :points="points"
                     v-on:chosen="addItem"
                     v-on:tentative="hoverItem"></auto-complete>
    </div>
    <hr>

    <!--Logo List-->
    <div v-if="selected.length" class="m-3 bd-logo-list">
      <p>Selected logos:</p>
      <div v-for="p in selected_points" :key="p.i"
           class="bd-point-item d-flex flex-row justify-content-between"
           @click="clickLogo(p)"
           @mouseover="hoverLogo(p)"
           @mouseout="unhoverLogo">
        <div class="text-truncate">
          <img :src="imageUrl(p)" class="m-1"/>
          <span>{{p.name}}</span>
        </div>
        <div class="pl-2">
          <button class="close"
                  @mouseover.stop=""
                  @click.stop="removeItem(p)">
            <span>&times;</span>
          </button>
        </div>
      </div>
    </div>

    <!--Footer-->
    <div v-if="selected.length" class="bd-panel-footer p-3">
      <div class="d-flex justify-content-between">
        <!--View Buttons-->
        <div class="btn-group btn-group-sm d-flex w-100">
          <b-btn class="btn btn-outline-secondary w-100"
                 v-b-tooltip.hover title="Display all logos"
                 :class="{active: view_mode === 1}"
                 @click="toggleAll">Show All</b-btn>
          <button class="btn btn-outline-secondary w-100 d-none"
                  :class="{active: view_mode === 2}"
                  @click="toggleSubset">Highlight</button>
          <b-btn class="btn btn-outline-secondary w-100"
                 v-b-tooltip.hover title="PCA over selected logos"
                 :class="{active: view_mode === 3}"
                 :disabled="!canPca()"
                 @click="reproject">Isolate</b-btn>
        </div>
        <div class="btn-group btn-group-sm ml-3">
          <b-btn class="btn btn-outline-secondary"
                 v-b-tooltip.hover title="Clear the selection"
                 @click="removeAll">
            <i class="fa fa-fw fa-trash"></i>
          </b-btn>
          <b-btn class="btn btn-outline-secondary"
                 v-b-tooltip.hover title="Save (not implemented yet!)">
            <i class="fa fa-fw fa-cloud-upload"></i>
          </b-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import AutoComplete from './AutoComplete.vue'
  import {store} from '../controllers/config'
  import _ from 'lodash'

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
      AutoComplete
    },
    data () {
      return {
        selection: '',
        selected: store.selected,
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
        console.log(store.selected, this.selected)
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
          this.$emit('detail', p)
        }
      },

      // interactions of the logo list
      clickLogo (p) {
        this.$emit('detail', p)
      },
      hoverLogo (p) {
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
  .bd-point-item {
    cursor: pointer;
    border-bottom: 1px solid rgba(0,0,0,.1);
  }

  .bd-point-item img {
    width: 32px;
    height: 32px;
  }

  .bd-logo-list {
    overflow-y: auto;
    height: calc(100vh - 15rem);
  }

  .bd-panel-footer {
    box-shadow: 0.5rem 0 2rem rgba(0,0,0,.03);
    border-top: 1px solid rgba(0,0,0,.1);
  }
</style>
