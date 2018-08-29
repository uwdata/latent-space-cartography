<template>
  <!--Save and Load Modal-->
  <b-modal id="modal-save" ref="modalSave"
           :title="load_only ? `Load a Group` : `Save / Load a Group`"
           @shown="fetchSaves" hide-footer>
    <!--Save-->
    <div v-if="!load_only">
      <div class="mb-3 text-center bd-subtitle text-uppercase">Save</div>
      <div class="d-flex justify-content-between">
        <input class="w-100" placeholder="(optional) title" v-model="current_alias">
        <button class="btn btn-primary ml-3"
                :disabled="saving"
                @click="clickSave">Save</button>
      </div>
      <hr>
    </div>
    <!--Load-->
    <div class="mb-3 text-center bd-subtitle text-uppercase"
         v-if="!load_only">Load</div>
    <div v-if="loading">Loading ...</div>
    <div v-if="!loading" class="bd-group mb-4">
      <!--Hint-->
      <div v-if="!groups.length" class="mt-5 mb-5 text-muted text-center">
        Nothing to load.
      </div>

      <!--List-->
      <div v-for="list in groups"  @click="load(list)"
           class="d-flex justify-content-between bd-group-item">
        <div>
          <group-thumb :list="list.list"></group-thumb>
          <b class="bd-link ml-2">{{list.alias || 'Untitled'}}</b>
          <small class="ml-2 text-muted">{{formatTime(list.timestamp)}}</small>
        </div>
        <div class="btn-group btn-group-sm">
          <b-btn class="btn btn-outline-secondary"
                 @click.stop="clickDelete(list.id)"
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
  import GroupThumb from './GroupThumbnail.vue'

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
    components: {
      GroupThumb
    },
    props: {
      load_only: {
        'default': false
      }
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

<style>
  .bd-group {
    overflow-y: auto;
    max-height: calc(50vh);
  }

  .bd-group-item {
    border-left: #eee 1px solid;
    border-right: #eee 1px solid;
    border-top: #eee 1px solid;
    padding: 10px;
    cursor: pointer;
  }

  .bd-group-item:last-child {
    border-bottom: #eee 1px solid;
  }

  .bd-group-item:hover {
    background-color: #fafafa;
  }

  .bd-link {
    cursor: pointer;
  }

  .bd-link:hover {
    color: #007bff;
    text-decoration: underline;
  }
</style>
