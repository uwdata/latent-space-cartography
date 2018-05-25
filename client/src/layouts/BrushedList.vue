<template>
  <div class="card mb-3" v-if="brushed.length">
    <div class="card-header d-flex justify-content-between">
      <div>Brushed</div>
      <div class="pl-3">
        <button class="btn btn-light btn-sm" @click="addAll()" v-if="shared.tab === 0">
          Add All
        </button>
      </div>
    </div>
    <div class="p-2">
      <div v-for="p in brushed" :key="p.i"
           @click="clickItem(p)"
           @mouseover="onHighlight(p, $event)"
           @mouseout="onHighlight()">
        <list-row :p="p" style="border: 0;">
          <button class="close p-2" style="font-size:1em;" @mouseover.stop="" @click.stop="addOne(p)">
            <i class="fa fa-plus"></i>
          </button>
        </list-row>
      </div>
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import _ from 'lodash'
  import ListRow from './ListRow.vue'

  let timer_handle = null

  export default {
    components: {ListRow},
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
        store.addToSelected([p.i])
      },
      addAll () {
        store.addToSelected(_.map(this.brushed, (p) => p.i))
      },
      clickItem (p) {
        store.state.detail_card = p
        store.state.clicked_point = p
      },
      onHighlight (p, event) {
        if (timer_handle) {
          clearTimeout(timer_handle)
        }


        if (p && event) {
          timer_handle = setTimeout(() => {
            p.clientX = event.clientX
            p.clientY = event.clientY
            store.state.detail = p
          }, 1000)
        } else {
          store.state.detail = p
        }

        this.chart.focusDot(p)
      },
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>
