<template>
  <div class="bd-point-item d-flex flex-row justify-content-between">
    <!--Logo: Left-->
    <div class="text-truncate" v-if="dset==='logo'">
      <img :src="imageUrl(p)" class="m-1"/>
      <span>{{p.name}}</span>
    </div>

    <!--Emoji: Left-->
    <div class="d-flex p-1" v-if="dset==='emoji'"
         style="max-width: calc(100% - 40px);">
      <div class="mr-1">
        <img :src="imageUrl(p)" class="m-1"/>
      </div>
      <div class="text-truncate">
        <div class="text-truncate bd-line-tight"><small>{{p.name}}</small></div>
        <div class="mt-1 text-muted text-truncate bd-text-xs">
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
  import {store, DATASET} from '../controllers/config'

  export default {
    name: 'ListRow',
    props: {
      p: {
        type: Object,
        required: true
      }
    },
    data () {
      return {
        dset: DATASET
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
  .bd-point-item {
    cursor: pointer;
    border-bottom: 1px solid rgba(0,0,0,.1);
  }

  .bd-point-item img {
    width: 32px;
    height: 32px;
  }

  .bd-text-xs {
    font-size: 0.7em;
  }

  .bd-line-tight {
    line-height: 1em;
  }
</style>
