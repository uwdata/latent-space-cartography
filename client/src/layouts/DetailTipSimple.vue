<template>
  <div class="d-flex bd-detail-simple" v-bind:style="getStyles()">
    <div class="pr-2">
      <img :src="imageUrl(detail_point)" />
    </div>
    <div class="pt-2 pr-2" v-if="long">
      {{detail_point.name}}
    </div>
  </div>
</template>

<script>
  import {store, DATASET} from '../controllers/config'
  export default {
    name: 'DetailTip',
    props: {
      detail_point: {
        required: true
      }
    },
    data () {
      return {
        long: DATASET === 'logo'
      }
    },
    methods: {
      // helper
      getX () {
        if (!this.detail_point) {
          return 0
        }

        let offset = this.long ? 90 : 32
        let x = Math.max(0, this.detail_point.screenX - offset)
        return x + 'px'
      },
      getY () {
        if (!this.detail_point) {
          return 0
        }

        let y = Math.max(0, this.detail_point.screenY - 74)
        return y + 'px'
      },
      getStyles () {
        return {
          top: this.getY(),
          left: this.getX(),
          minWidth: (this.long ? 180 : 0) + 'px'
        }
      },
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>

<style>
  .bd-detail-simple {
    max-width: 240px;
    max-height: 64px;
    background-color: #fff;
    position: absolute;
    z-index: 5000;
    line-height: 1.2em;
  }
</style>
