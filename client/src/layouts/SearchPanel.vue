<template>
  <div>
    <div v-if="selected.length">
      <div class="mb-3 btn-group d-flex">
        <button class="btn btn-secondary w-100">Show All</button>
        <button class="btn btn-secondary w-100" :class="{disabled: subset}"
                @click="toggleSubset">Highlight</button>
        <button class="btn w-100 btn-secondary">Re-project</button>
      </div>
    </div>
    <auto-complete v-model="selection" v-on:chosen="addItem"
                   :points="points"></auto-complete>
    <hr>
    <div v-if="selected.length">
      <p>Selected logos:</p>
      <div v-for="p in selected" :key="p.i"
           class="bd-point-item d-flex flex-row justify-content-between"
           @mouseover="hoverLogo(p)" @mouseout="unhoverLogo">
        <div class="text-truncate">
          <img :src="imageUrl(p)" class="m-1"/>
          <span>{{p.name}}</span>
        </div>
        <div class="pl-2">
          <button class="close" @click="removeItem(p)">
            <span>&times;</span>
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
      toggleSubset () {
        this.subset = !this.subset
        this.$emit('subset', this.subset ? this.selected : null)
      },
      addItem (p) {
        this.selected.push(p)
        this.selected = _.uniqBy(this.selected, (p) => p.i)
      },
      removeItem (p) {
        this.selected = _.filter(this.selected, (s) => s.i !== p.i)
      },
      imageUrl (p) {
        return store.getImageUrl(p.i)
      },
      hoverLogo (p) {
        this.$emit('highlight', p)
      },
      unhoverLogo () {
        this.$emit('highlight', null)
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
</style>
