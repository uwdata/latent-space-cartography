<template>
  <div id="app">
    <router-view
        class="view"
        transition
        transition-mode="out-in">
    </router-view>
  </div>
</template>

<script>
  export default {
    name: 'app',
    data () {
      return {
      }
    }
  }
</script>

<style>
  @import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
</style>
