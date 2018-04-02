<template>
  <div>
    <auto-complete v-model="selection" v-on:chosen="addItem"
                   :points="points"></auto-complete>
    <hr>
    <div v-if="selected.length">
      <p>Selected logos:</p>
      <div v-for="p in selected" :key="p.i" class="bd-point-item">
        <div class="text-truncate">
          <img :src="imageUrl(p)" class="m-1"/>
          <span>{{p.name}}</span>
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
        selected: []
      }
    },
    methods: {
      addItem (p) {
        this.selected.push(p)
        this.selected = _.uniqBy(this.selected, (p) => p.i)
      },
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
</style>
