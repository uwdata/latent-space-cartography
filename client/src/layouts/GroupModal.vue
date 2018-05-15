<template>
  <!--Choose Group Modal-->
  <b-modal id="modal-group" ref="modalGroup"
           title="Choose a Group ..."
           @shown="fetchSaves">
    <div v-if="loading">Loading ...</div>
    <div v-if="!loading" class="bd-group">
      <div v-for="list in groups" class="d-flex justify-content-between bd-group-item">
        <div>
          <div class="bd-image-container">
            <img v-for="pi in list.list.slice(0, 6)" :src="imageUrl(pi)"
                 class="bd-image-inline"/>
          </div>
          <b @click="clickGroup(list)" v-b-tooltip.hover title="Set as endpoint"
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

  export default {
    name: 'GroupModal',
    data () {
      return {
        loading: false,
        groups: []
      }
    },
    methods: {
      // load the list of groups
      fetchSaves () {
        this.loading = true
        store.getLogoLists()
          .then((list) => {
            this.loading = false
            this.groups = list
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
