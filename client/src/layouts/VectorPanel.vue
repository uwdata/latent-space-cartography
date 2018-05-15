<template>
  <div v-if="tab.index === 1">
    <!--Tabs-->
    <b-nav justified tabs class="ml-3 mr-3 mt-1">
      <b-nav-item @click="clickTab">Groups</b-nav-item>
      <b-nav-item active>Vectors</b-nav-item>
    </b-nav>

    <!--Top Division-->
    <div class="m-3 d-flex">
      <!--Start-->
      <div class="d-inline-block" @click="which = 'start'"
           title="Choose a starting group"
           v-b-modal.modal-group v-b-tooltip.hover>
        <button v-if="!start" class="btn btn-outline-secondary">
          <i class="fa fa-fw fa-circle-o"></i>
        </button>
        <group-thumb v-if="start" :group="start" :width="4"
                     class="m-1"></group-thumb>
      </div>

      <!--Middle-->
      <div class="d-inline-block w-100">
        <div class="bd-arrow h-50"></div>
        <button class="btn btn-secondary btn-sm bd-arrow-btn"
                @click="clickAdd" :disabled="!start || !end">Add</button>
      </div>

      <!--End-->
      <div class="d-inline-block" @click="which = 'end'"
           title="Choose an ending group"
           v-b-modal.modal-group v-b-tooltip.hover>
        <group-thumb v-if="end" :group="end" :width="4"
                     class="m-1"></group-thumb>
        <button v-if="!end" class="btn btn-outline-secondary">
          <i class="fa fa-fw fa-circle-o"></i>
        </button>
      </div>
    </div>
    <hr>

    <!--Modal-->
    <group-modal v-on:clickGroup="clickGroup"></group-modal>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import GroupModal from './GroupModal.vue'
  import GroupThumb from './GroupThumbnail.vue'

  export default {
    name: 'VectorPanel',
    props: {
      latent_dim: {
        type: Number,
        required: true
      }
    },
    components: {
      GroupModal,
      GroupThumb
    },
    data () {
      return {
        start: null,
        end: null,
        which: 'start',
        vectors: [],
        tab: store.tab
      }
    },
    methods: {
      // the tab at top
      clickTab () {
        store.tab.index = 0
      },
      // when a group is selected
      clickGroup (group) {
        this[this.which] = group
      },
      // when the button "Add" is clicked
      clickAdd () {
        if (!this.start || !this.end) {
          return
        }

        store.createVector(this.start.id, this.end.id)
          .then(() => {
            this.start = null
            this.end = null
          }, (e) => {
            alert(e)
          })
      }
    }
  }
</script>

<style>
  .bd-arrow {
    border-bottom: 1px dotted #6c757d;
    margin-left: 15px;
    margin-right: 15px;
  }

  .bd-arrow-btn {
    position: absolute;
    left: 40%;
    margin-top: -15px;
  }
</style>
