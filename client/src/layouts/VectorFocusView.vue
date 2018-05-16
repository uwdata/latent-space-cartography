<template>
  <div>
    <!--Top Division-->
    <div class="d-flex">
      <!--Back Button-->
      <div @click="clickBack" title="Back to Vector List"
           class="bd-btn-trans p-3" v-b-tooltip.hover>
        <i class="fa fa-fw fa-arrow-left text-muted"></i>
      </div>

      <!--Title-->
      <div class="p-3 w-100 text-center text-truncate">
        {{focus.description || 'Untitled Vector'}}
      </div>

      <!--Right Buttons-->
      <div>
        <div title="Delete Vector" class="bd-btn-trans p-3"
             v-b-tooltip.hover>
          <i class="fa fa-fw fa-trash-o text-muted"></i>
        </div>
      </div>
    </div>
    <hr class="mt-0">

    <!--Main View-->
    <div>
      <!--Start Group-->
      <div class="bd-panel-card m-3" @click="viewGroup(focus.list_start)">
        <div>
          <b>Start:</b>
          <span>{{focus.alias_start}}</span>
        </div>
        <div class="mt-3">
          <img v-for="pi in focus.list_start.slice(0, totalImage)"
               :src="imageUrl(pi)" class="bd-img-box"/>
          <div class="text-right">
            <small class="text-muted" v-if="startMore">
              ... {{startMore}} more
            </small>
          </div>
        </div>
      </div>

      <!--End Group-->
      <div class="bd-panel-card m-3" @click="viewGroup(focus.list_end)">
        <div>
          <b>End:</b>
          <span>{{focus.alias_end}}</span>
        </div>
        <div class="mt-3">
          <img v-for="pi in focus.list_end.slice(0, totalImage)"
               :src="imageUrl(pi)" class="bd-img-box"/>
          <div class="text-right">
            <small class="text-muted" v-if="endMore">
              ... {{endMore}} more
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import _ from 'lodash'

  export default {
    name: 'VectorFocusView',
    props: {
      focus: {
        type: Object,
        default: null
      }
    },
    data () {
      return {
        totalImage: 20,
      }
    },
    computed: {
      startMore: function () {
        return Math.max(0, this.focus.list_start.length - this.totalImage)
      },
      endMore: function () {
        return Math.max(0, this.focus.list_end.length - this.totalImage)
      }
    },
    methods: {
      // go back to the list
      clickBack () {
        this.$emit('back')
      },

      viewGroup (list) {
        while (store.selected.length) {
          store.selected.splice(0, 1)
        }

        _.each(list, (i) => {
          store.selected.push(i)
        })

        store.tab.index = 0
      },

      // helper
      imageUrl (i) {
        return store.getImageUrl(i)
      }
    }
  }
</script>

<style>
  .bd-btn-trans {
    display: inline-block;
    cursor: pointer;
  }
  .bd-btn-trans:hover {
    background-color: #eee;
  }

  .bd-panel-card {
    border: #ddd 1px solid;
    padding: 15px 15px 20px;
    background-color: #fff;
    cursor: pointer;
  }

  .bd-panel-card:hover {
    background-color: #fafafa;
  }

  .bd-img-box {
    width: 10%;
    height: 10%;
  }
</style>
