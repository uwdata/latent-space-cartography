<template>
  <div class="bd-list-row d-flex flex-row justify-content-between"
       :style="styles" @mouseover="hovered=true" @mouseout="hovered=false">

    <div class="d-flex p-1"
         style="max-width: calc(100% - 40px);">
      <div class="mr-1" v-if="show_image">
        <img :src="imageUrl(p)" class="m-1"/>
      </div>
      <div class="text-truncate">
        <div class="text-truncate bd-line-tight"><small>{{p.name}}</small></div>
        <div class="mt-1 text-muted text-truncate bd-text-xs" v-if="show_platform">
          {{p.platform}} {{p.version}}
        </div>
      </div>
    </div>

    <!--Button Slot-->
    <div class="pl-2 d-flex align-items-center">
      <slot></slot>
    </div>
  </div>
</template>

<script>
  import {store, CONFIG} from '../controllers/config'
  import _ from 'lodash'

  export default {
    name: 'ListRow',
    props: {
      p: {
        type: Object,
        required: true
      },
      hoverColor: {
        type: String,
        default: '#fafafa'
      }
    },
    computed: {
      styles () {
        return this.hovered ? {backgroundColor: this.hoverColor} : {}
      },
      show_platform () {
        let meta = CONFIG.schema.meta
        return _.find('platform', meta) && _.find('version', meta)
      }
    },
    data () {
      return {
        hovered: false,
        dset: CONFIG.dataset,
        show_image: CONFIG.data_type === 'image'
      }
    },
    methods: {
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>

<style>
  .bd-text-xs {
    font-size: 0.7em;
  }

  .bd-line-tight {
    line-height: 1em;
  }

  .bd-list-row {
    cursor: pointer;
    border-bottom: 1px solid rgba(0,0,0,.1);
  }

  .bd-list-row img {
    width: 32px;
    height: 32px;
  }
</style>
