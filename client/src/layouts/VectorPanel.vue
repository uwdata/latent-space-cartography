<template>
  <div v-if="tab.index === 1">
    <!--Tabs-->
    <b-nav justified tabs class="ml-3 mr-3 mt-1">
      <b-nav-item @click="clickTab">Groups</b-nav-item>
      <b-nav-item active>Vectors</b-nav-item>
    </b-nav>

    <div>
      Vector Panel
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import GroupModal from './GroupModal.vue'

  export default {
    name: 'VectorPanel',
    components: {
      GroupModal
    },
    data () {
      return {
        tab: store.tab
      }
    },
    methods: {
      // the tab at top
      clickTab () {
        store.tab.index = 0
      }
    }
  }
</script>
