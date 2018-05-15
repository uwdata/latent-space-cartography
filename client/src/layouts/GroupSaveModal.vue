<template>
  <!--Save and Load Modal-->
  <b-modal id="modal-save" ref="modalSave"
           title="Save and Load"
           @shown="fetchSaves">
    <div class="d-flex justify-content-between">
      <input class="w-100" placeholder="(optional) title" v-model="current_alias">
      <button class="btn btn-primary ml-3"
              :disabled="saving"
              @click="clickSave">Save</button>
    </div>
    <hr>
    <div v-if="loading">Loading ...</div>
    <div v-if="!loading">
      <div v-for="list in groups" class="d-flex justify-content-between">
        <div>
          <b>{{list.alias || 'Untitled'}}</b>
          <span class="ml-2 text-muted">{{formatTime(list.timestamp)}}</span>
        </div>
        <div class="btn-group btn-group-sm">
          <b-btn class="btn btn-outline-secondary"
                 @click="load(list)"
                 v-b-tooltip.hover title="Load">
            <i class="fa fa-fw fa-cloud-download"></i>
          </b-btn>
          <b-btn class="btn btn-outline-secondary"
                 @click="clickDelete(list.id)"
                 v-b-tooltip.hover title="Delete">
            <i class="fa fa-fw fa-trash-o"></i>
          </b-btn>
        </div>
      </div>
    </div>
  </b-modal>
</template>

<script>
  import {store} from '../controllers/config'
  import moment from 'moment'
  import _ from 'lodash'

  export default {
    name: 'GroupSaveModal',
    data () {
      return {
        current_alias: '',
        loading: false,
        saving: false,
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

      // button "save"
      clickSave () {
        this.saving = true
        store.saveLogoList(store.selected, this.current_alias)
          .then(() => {
            this.saving = false
            this.$refs.modalSave.hide()
          }, () => {
            this.saving = false
            //TODO: handle error
          })
      },

      // when a group is clicked in the Save/Load modal
      load (group) {
        this.$emit('load', group)
        this.$refs.modalSave.hide()
      },

      // delete the group
      clickDelete (id) {
        store.deleteLogoList(id)
          .then(() => {
            let i = _.findIndex(this.groups, (g) => g.id === id)
            this.groups.splice(i, 1)
          }, () => {
            //TODO: handle error
          })
      },

      formatTime (t) {
        return moment(t).fromNow()
      }
    }
  }
</script>
