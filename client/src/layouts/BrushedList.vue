<template>
  <div class="card mb-3" v-if="brushed.length">
    <div class="card-header">Brushed</div>
    <div class="p-2">
      <div v-for="p in brushed" :key="p.i"
           @click="setDetail(p)"
           @mouseover="onHighlight(p)"
           @mouseout="onHighlight()"
           class="bd-point-item d-flex flex-row justify-content-between">
        <div class="text-truncate">
          <img :src="imageUrl(p)" class="m-1"/>
          <span>{{p.name}}</span>
        </div>
        <div class="pl-2 d-flex align-items-center">
          <button class="close" style="font-size:1em;" @click.stop="addOne(p)">
            <i class="fa fa-plus"></i>
          </button>
        </div>
      </div>
      <button class="btn-block btn btn-light mt-3 mb-2"
              @click="addAll()">Add All</button>
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import _ from 'lodash'

  export default {
    name: 'BrushedList',
    props: {
      chart: {
        required: true
      },
      brushed: {
        type: Array,
        required: true
      }
    },
    data () {
      return {
        shared: store.state
      }
    },
    methods: {
      // Add brushed points to the selected list
      addOne (p) {
        if (!_.includes(store.selected, p.i)) {
          store.selected.push(p.i)
        }
      },
      addAll () {
        _.each(this.brushed, (p) => this.addOne(p))
      },
      setDetail (p) {
        this.shared.detail = p
      },
      onHighlight (p) {
        this.chart.focusDot(p)
      },
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>
