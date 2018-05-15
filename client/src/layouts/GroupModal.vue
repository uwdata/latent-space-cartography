<template>
  <!--Choose Group Modal-->
  <b-modal id="modal-group" ref="modalGroup"
           title="Choose a Group ..."
           @shown="fetchSaves">
    <div v-if="loading">Loading ...</div>
    <div v-if="!loading" class="bd-group">
      <div v-for="list in groups" class="d-flex justify-content-between bd-group-item">
        <div>
          <group-thumb :list="list.list"></group-thumb>
          <b @click="clickGroup(list)"
             class="bd-link ml-2">{{list.alias || 'Untitled'}}</b>
          <small class="ml-2 text-muted">{{formatTime(list.timestamp)}}</small>
        </div>
      </div>
    </div>
  </b-modal>
</template>

<script>
  import {store} from '../controllers/config'
  import moment from 'moment'
  import GroupThumb from './GroupThumbnail.vue'

  export default {
    name: 'GroupModal',
    data () {
      return {
        loading: false,
        groups: []
      }
    },
    components: {
      GroupThumb
    },
    methods: {
      // load the list of groups
      fetchSaves () {
        this.loading = true
        store.getLogoLists()
          .then(() => {
            this.loading = false
            this.groups = store.groups
          }, () => {
            this.loading = false
            //TODO: handle error
          })
      },

      // when a group is clicked
      clickGroup (group) {
        this.$emit('clickGroup', group)
        this.$refs.modalGroup.hide()
      },

      imageUrl (i) {
        return store.getImageUrl(i)
      },

      formatTime (t) {
        return moment(t).fromNow()
      }
    }
  }
</script>
