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
             v-b-tooltip.hover @click="clickDelete">
          <i class="fa fa-fw fa-trash-o text-muted"></i>
        </div>
      </div>
    </div>
    <hr class="mt-0">

    <!--Main View-->
    <div class="bd-focus-panel-body">
      <div class="d-flex m-3">
        <!--Start Group-->
        <div class="bd-panel-card bd-pointer" @click="viewGroup(focus.list_start)">
          <div>
            <b>Start:</b>
            <div class="text-truncate">{{focus.alias_start}}</div>
          </div>
          <div class="mt-2">
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
        <div class="bd-panel-card bd-pointer ml-3" @click="viewGroup(focus.list_end)">
          <div>
            <b>End:</b>
            <div class="text-truncate">{{focus.alias_end}}</div>
          </div>
          <div class="mt-2">
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

      <!--Apply Analogy-->
      <div class="bd-panel-card m-3" v-if="detail">
        <div class="d-flex">
          <div class="mr-2">
            <img :src="imageUrl(detail.i)" style="width: 3rem; height: 3rem;" />
          </div>
          <div>
            <b>Selected:</b>
            <div class="text-truncate">{{detail.name}}</div>
          </div>
        </div>
        <div class="mt-3">
          <button class="btn btn-light btn-block" @click="applyAnalogy">Apply Analogy</button>
        </div>
      </div>

      <!--Vector Details-->
      <div class="d-flex m-3" v-if="analogy && original">
        <div class="w-50 d-flex flex-column mt-3">
          <p class="text-right"><b>Original</b></p>
          <div v-for="d in original" class="div-48 text-right"
               @mouseover="mouseOverImage(d)" @mouseleave="mouseLeaveImage(d)">
            <span class="text-muted mr-2">{{d.neighbors}}</span>
            <img :src="imageUrl(d.nearest)" class="img-48 mr-2" v-if="showNearest === d.image"/>
            <img :src="`/build/${d.image}`" class="img-48" />
          </div>
        </div>
        <div class="w-50 d-flex flex-column mt-3 ml-3">
          <p><b>Analogy</b></p>
          <div v-for="d in analogy" class="div-48"
               @mouseover="mouseOverImage(d)" @mouseleave="mouseLeaveImage(d)">
            <img :src="`/build/${d.image}`" class="img-48" />
            <img :src="imageUrl(d.nearest)" class="img-48 ml-2" v-if="showNearest === d.image"/>
            <span class="text-muted ml-2">{{d.neighbors}}</span>
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
      latent_dim: {
        type: Number,
        required: true
      },
      detail: {
        required: true
      },
      focus: {
        required: true
      },
      chart: {
        required: true
      }
    },
    data () {
      return {
        totalImage: 5,
        analogy: null,
        original: null,
        showNearest: ''
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

      clickDelete () {
        store.deleteVector(this.focus.id)
          .then(() => {
            this.$emit('back', true)
          }, (e) => {
            alert(e)
          })
      },

      mouseOverImage (d) {
        this.showNearest = d.image
      },

      mouseLeaveImage (d) {
        this.showNearest = d.image
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

      applyAnalogy () {
        // FIXME: hack
        this.original = this.focus.line

        if (this.analogy) {
          this.chart._vectors.removeOne(this.analogy)
        }
        store.applyAnalogy(this.latent_dim, this.detail.i,
          this.focus.start, this.focus.end)
          .then((line) => {
            this.analogy = line
            this.chart._vectors.drawOne(line)
          }, (e) => {
            alert(e)
          })
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
  }

  .bd-panel-card:hover {
    background-color: #fafafa;
  }

  .bd-img-box {
    width: 20%;
    height: 20%;
  }

  .bd-pointer {
    cursor: pointer;
  }

  .bd-focus-panel-body {
    height: calc(100vh - 12rem);
    overflow-y: auto;
  }

  .img-48 {
    width: 48px;
    height: 48px;
  }

  .div-48 {
    line-height: 48px;
    font-size: 0.7em;
  }
</style>
