<template>
  <div class="d-flex flex-row">
    <div class="d-flex flex-column pl-3 pt-3">
      <button class="btn btn-outline-secondary img-48"
              @click="clickStart"
              v-b-modal.modal-group>
        <i v-if="!groups[0]" class="fa fa-fw fa-circle-o"></i>
        {{groups[0]}}
      </button>
      <div style="min-height: 432px" class="mt-3 mb-3 d-flex">
        <div v-if="loading">Generating ...</div>
        <div v-if="!loading" class="d-flex flex-column">
          <div v-for="img in generated">
            <img :src="`/build/${img}`" class="img-48" />
          </div>
        </div>
        <div v-if="!loading" class="d-flex flex-column text-muted pl-1">
          <div v-for="count in generated_neighbors">
            <div class="align-middle div-48">{{count}}</div>
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

    <div v-if="groups[0] && groups[1]" class="d-flex flex-column p-3">
      <div class="img-48" style="border: 1px solid #eee">
        <i v-if="!detail" class="fa fa-fw fa-question"></i>
        <img v-if="detail" :src="getUrl(detail)" class="img-48" />
      </div>
      <div style="min-height: 432px" class="mt-3 mb-3 d-flex">
        <div v-if="loading_analogy">Generating ...</div>
        <div v-if="!loading_analogy" class="d-flex flex-column">
          <div v-for="img in analogy">
            <img :src="`/build/${img}`" class="img-48" />
          </div>
        </div>
        <div v-if="!loading_analogy" class="d-flex flex-column text-muted pl-1">
          <div v-for="count in analogy_neighbors">
            <div class="align-middle div-48 ">{{count}}</div>
          </div>
        </div>
      </div>
      <div class="img-48"></div>

      <button class="btn btn-warning mt-3" style="width: 48px"
              :disabled="!groups[0] && !groups[1]"
              @click="runAnalogy">
        Go
      </button>
    </div>

    <div class="p-3">
      <button class="btn btn-secondary btn-sm"
              :disabled="!analogy_vector || analogy_vector.length != latent_dim"
              @click="project">Project</button>
    </div>

    <group-modal v-on:clickGroup="clickGroup"></group-modal>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import GroupModal from './GroupModal.vue'

  export default {
    name: 'InterpolatePanel',
    props: {
      latent_dim: {
        type: Number,
        required: true
      },
      detail: {
        required: true
      }
    },
    components: {
      GroupModal
    },
    data (){
      return {
        groups: [null, null],
        trigger: 0,
        loading: false,
        loading_analogy: false,
        analogy_vector: null,
        generated: [],
        generated_neighbors: [],
        analogy: [],
        analogy_neighbors: []
      }
    },
    methods: {
      runAnalogy () {
        this.loading_analogy = true
        store.applyAnalogy(this.latent_dim, this.detail.i, this.analogy_vector)
          .then((all) => {
            this.loading_analogy = false
            this.analogy = all[0]
            this.analogy_neighbors = all[1]
          }, () => {
            this.loading_analogy = false
          })
      },
      interpolate () {
        this.loading = true
        store.interpolateBetween(this.groups, this.latent_dim)
          .then((all) => {
            this.loading = false
            this.generated = all[0]
            this.analogy_vector = all[1]
            this.generated_neighbors = all[2]

            console.log('generated_neighbors', this.generated_neighbors)
          }, () => {
            this.loading = false
          })
      },
      project () {
        this.$emit('project', this.analogy_vector)
      },
      reset () {
        this.$emit('reset')
      },
      clickStart () {
        // since they share a modal, we distinguish the trigger
        this.trigger = 0
      },
      clickEnd () {
        this.trigger = 1
      },
      clickGroup (group) {
        this.groups[this.trigger] = group.id
      },
      getUrl (point) {
        return store.getImageUrl(point.i)
      }
    }
  }
</script>

<style>
  .img-48 {
    width: 48px;
    height: 48px;
  }

  .div-48 {
    line-height: 48px;
    font-size: 0.7em;
  }
</style>
