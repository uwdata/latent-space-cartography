<template>
  <div class="row mt-5">
    <div class="col-2"></div>
    <div class="col-8 text-center">
      <h3 class="mb-3">Some Title.</h3>
      This is a description.
      <div id="container" class="mt-3"></div>
    </div>
    <div class="col-2"></div>
  </div>
</template>

<script>
  import {draw} from '../controllers/scatter'

  export default {
    name: 'ScatterPage',
    data () {
      return {}
    },
    mounted: function () {
      draw('#container')
    }
  }
</script>
