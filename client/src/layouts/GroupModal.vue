<template>
  <!--Choose Group Modal-->
  <b-modal id="modal-group" ref="modalGroup"
           title="Choose a Group ..."
           @shown="fetchSaves">
    <div v-if="loading">Loading ...</div>
    <div v-if="!loading">
      <div v-for="list in groups" class="d-flex justify-content-between">
        <a @click="clickGroup(list)" href="#">
          <div>
            <span class="text-muted mr-1">{{list.id}}.</span>
            <b>{{list.alias || 'Untitled'}}</b>
            <span class="ml-2 text-muted">{{formatTime(list.timestamp)}}</span>
          </div>
        </a>
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

      formatTime (t) {
        return moment(t).fromNow()
      }
    }
  }
</script>
