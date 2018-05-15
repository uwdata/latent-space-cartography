<template>
  <div class="bd-image-container" :style="containerStyle">
    <img v-for="pi in group.list.slice(0, totalImages)" :src="imageUrl(pi)"
         class="bd-image-inline"/>
  </div>
</template>

<script>
  import {store} from '../controllers/config'

  export default {
    name: 'GroupThumbnail',
    props: {
      width: {
        type: Number,
        default: 3
      },
      height: {
        type: Number,
        default: 2
      },
      group: {
        type: Object,
        required: true
      }
    },
    computed: {
      totalImages: function () {
        return this.width * this.height
      },
      containerStyle: function () {
        return {
          maxWidth: `${this.width}rem`,
          minWidth: `${this.width}rem`
        }
      }
    },
    methods: {
      imageUrl (i) {
        return store.getImageUrl(i)
      }
    }
  }
</script>

<style>
  .bd-image-inline {
    width: 1rem;
    height: 1rem;
  }

  .bd-image-container {
    display: inline-block;
    line-height: 0.8rem;
  }
</style>
