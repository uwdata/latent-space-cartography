<template>
  <div>
    <auto-complete v-model="selection" :points="points"></auto-complete>
    <p>{{selection}}</p>
  </div>
</template>

<script>
  import AutoComplete from './AutoComplete.vue'

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
        selection: ''
      }
    }
  }
</script>
