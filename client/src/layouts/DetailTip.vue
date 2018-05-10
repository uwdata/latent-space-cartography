<template>
  <div class="d-flex bd-detail" v-bind:style="{top: getY(), left: getX()}">
    <div class="pr-2">
      <img :src="imageUrl(detail_point)" />
    </div>
    <div class="pt-2 pr-2">
      {{detail_point.name}}
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  export default {
    name: 'DetailTip',
    props: {
      detail_point: {
        required: true
      }
    },
    methods: {
      // helper
      getX () {
        if (!this.detail_point) {
          return 0
        }

        let x = Math.max(0, this.detail_point.screenX - 90)
        return x + 'px'
      },
      getY () {
        if (!this.detail_point) {
          return 0
        }

        let y = Math.max(0, this.detail_point.screenY - 74)
        return y + 'px'
      },
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>

<style>
  .bd-detail {
    min-width: 180px;
    max-width: 240px;
    max-height: 64px;
    background-color: #fff;
    position: absolute;
    z-index: 5000;
    line-height: 1.2em;
  }
</style>
