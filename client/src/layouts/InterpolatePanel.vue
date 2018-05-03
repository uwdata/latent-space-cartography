<template>
  <div>
    <div class="d-flex flex-column p-3">
      <button class="btn btn-outline-secondary img-48"
              @click="clickStart"
              v-b-modal.modal-group>
        <i v-if="!groups[0]" class="fa fa-fw fa-circle-o"></i>
        {{groups[0]}}
      </button>
      <div style="min-height: 384px" class="mt-3 mb-3">
        <div v-if="loading">Generating ...</div>
        <div v-if="!loading" class="d-flex flex-column">
          <div v-for="img in generated">
            <img :src="`/build/${img}`" class="img-48" />
          </div>
        </div>
      </div>
      <button class="btn btn-outline-secondary img-48"
              @click="clickEnd"
              v-b-modal.modal-group>
        <i v-if="!groups[1]" class="fa fa-fw fa-circle-o"></i>
        {{groups[1]}}
      </button>

      <button class="btn btn-warning mt-3" style="width: 48px"
              :disabled="!groups[0] && !groups[1]"
              @click="interpolate">
        Go
      </button>
    </div>

    <!--TODO: refactor this modal-->
    <b-modal id="modal-group" ref="modalGroup"
             title="Choose a Group ..."
             @shown="fetchSaves">
      <div v-if="loading_list">Loading ...</div>
      <div v-if="!loading_list">
        <div v-for="list in logo_lists" class="d-flex justify-content-between">
          <a @click="clickGroup(list.id)" href="#">
            <div>
              <span class="text-muted mr-1">{{list.id}}.</span>
              <b>{{list.alias || 'Untitled'}}</b>
              <span class="ml-2 text-muted">{{formatTime(list.timestamp)}}</span>
            </div>
          </a>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import moment from 'moment'

  export default {
    name: 'InterpolatePanel',
    props: {
      latent_dim: {
        type: Number,
        required: true
      }
    },
    data (){
      return {
        groups: [null, null],
        trigger: 0,
        loading: false,
        loading_list: false,
        logo_lists: [],
        generated: []
      }
    },
    methods: {
      interpolate () {
        this.loading = true
        store.interpolateBetween(this.groups, this.latent_dim)
          .then((data) => {
            this.loading = false
            this.generated = data
          }, () => {
            this.loading = false
          })
      },
      fetchSaves () {
        this.loading_list = true
        store.getLogoLists()
          .then((list) => {
            this.loading_list = false
            this.logo_lists = list
          }, () => {
            this.loading_list = false
            //TODO: handle error
          })
      },
      clickStart () {
        // since they share a modal, we distinguish the trigger
        this.trigger = 0
      },
      clickEnd () {
        this.trigger = 1
      },
      clickGroup (id) {
        this.groups[this.trigger] = id
        this.$refs.modalGroup.hide()
      },
      formatTime (t) {
        return moment(t).fromNow()
      }
    }
  }
</script>

<style>
  .img-48 {
    width: 48px;
    height: 48px;
  }
</style>
