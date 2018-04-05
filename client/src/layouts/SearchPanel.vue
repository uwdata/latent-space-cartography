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
      <div v-for="p in selected" :key="p.i"
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
        <div class="btn-group d-flex w-100">
          <button class="btn btn-secondary w-100" :class="{disabled: subset}"
                  @click="toggleSubset">Highlight</button>
          <button class="btn w-100 btn-secondary"
                  @click="reproject">Re-project</button>
        </div>
        <div class="btn-group ml-3">
          <button class="btn btn-secondary">
            <i class="fa fa-cloud-upload"></i>
          </button>
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
        selected: [],
        subset: false
      }
    },
    methods: {
      // button "highlight"
      toggleSubset () {
        this.subset = !this.subset
        this.$emit('subset', this.subset ? this.selected : null)
      },

      // button "re-project"
      reproject () {
        // TODO: tell user you can't PCA with less than 3 points
        if (this.selected.length > 3) {
          this.$emit('reproject', _.map(this.selected, (p) => p.i))
        }
      },

      // modify the list
      addItem (p) {
        this.selected.push(p)
        this.selected = _.uniqBy(this.selected, (p) => p.i)
      },
      removeItem (p) {
        this.selected = _.filter(this.selected, (s) => s.i !== p.i)
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
        this.$emit('highlight', p)
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
