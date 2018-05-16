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
        <group-thumb v-if="start" :list="start.list" :width="4"
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
        <group-thumb v-if="end" :list="end.list" :width="4"
                     class="m-1"></group-thumb>
        <button v-if="!end" class="btn btn-outline-secondary">
          <i class="fa fa-fw fa-circle-o"></i>
        </button>
      </div>
    </div>

    <!--Vector List-->
    <div class="bd-vector-list m-3 mt-4">
      <div v-for="v in vectors" @click="focusVector(v)"
           class="d-flex bd-vector">
        <div class="mr-2 d-flex flex-column">
          <i class="fa fa-fw fa-circle-o bd-arrow-end mt-1"></i>
          <div class="bd-arrow-vertical h-100"></div>
          <i class="fa fa-fw fa-circle-o bd-arrow-end"></i>
        </div>
        <div class="w-100">
          <div>
            <group-thumb :list="v.list_start" :width="4" :height="1"></group-thumb>
            <span class="ml-2 text-truncate">{{v.alias_start}}</span>
          </div>
          <div>
            <group-thumb :list="v.list_end" :width="4" :height="1"></group-thumb>
            <span class="ml-2 text-truncate">{{v.alias_end}}</span>
          </div>
        </div>
      </div>
    </div>

    <!--Modal-->
    <group-modal v-on:clickGroup="clickGroup"></group-modal>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import moment from 'moment'
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
    mounted: function () {
      this.fetchVectors()
    },
    methods: {
      fetchVectors () {
        store.getVectors()
          .then((vectors) => {
            this.vectors = vectors
          }, (e) => {
            alert(e)
          })
      },
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
            this.fetchVectors() // TODO: only query for a single vector
          }, (e) => {
            alert(e)
          })
      },
      focusVector (vector) {
        this.$emit('focus', vector.start, vector.end)
      },
      formatTime (t) {
        return moment(t).fromNow()
      }
    }
  }
</script>

<style>
  .bd-vector {
    border-left: #ddd 1px solid;
    border-right: #ddd 1px solid;
    border-top: #ddd 1px solid;
    padding: 15px;
    background-color: #fff;
    cursor: pointer;
  }
  .bd-vector:last-child {
    border-bottom: #ddd 1px solid;
  }
  .bd-vector:hover {
    background-color: #fafafa;
  }

  .bd-vector-list {
    overflow-y: auto;
    height: calc(100vh - 13rem);
  }

  .bd-arrow {
    border-bottom: 1px dotted #6c757d;
    margin-left: 15px;
    margin-right: 15px;
  }

  .bd-arrow-vertical {
    border-right: 2px dotted #6c757d;
    width: calc(50% + 1px);
  }

  .bd-arrow-end {
    color: #8c959d;
    font-size: 0.9em;
  }

  .bd-arrow-btn {
    position: absolute;
    left: 40%;
    margin-top: -15px;
  }
</style>
