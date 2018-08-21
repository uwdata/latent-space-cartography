<template>
  <div v-if="ready" class="d-inline-block float-right">
    <b-btn class="btn-light" v-b-modal.modal-filter
           v-b-tooltip.hover title="Filter">
      <i class="fa fa-filter"></i>
    </b-btn>

    <b-modal id="modal-filter" ref="modalFilter" size="lg"
             title="Filter" hide-footer>
      <div class="m-3" v-if="active_fields.length" >
        <div v-for="(f, idx) in active_fields" class="mb-2 d-flex">
          <div>
            <multiselect v-model="active_fields[idx]" :options="getAvalFields()"
                         :show-labels="false" style="min-width: 150px"></multiselect>
          </div>
          <div class="ml-2">
            <multiselect v-model="active[f]" :options="all[f]" :multiple="true"
                         :close-on-select="false" :preserve-search="true"
                         :show-labels="false"
                         :hide-selected="true" placeholder="Pick values ...">
            </multiselect>
          </div>
          <button class="btn btn-link ml-2" @click="clickRemove(idx)">
            remove
          </button>
        </div>
      </div>
      <b-btn class="btn-light btn-lg m-3" v-if="getAvalFields().length"
             @click="clickAdd"
             v-b-tooltip.hover title="Add a Criteria">
        <i class="fa fa-plus"></i>
      </b-btn>
    </b-modal>
  </div>
</template>

<script>
  import {CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import Multiselect from 'vue-multiselect'

  export default {
    name: 'FilterButton',
    props: {
      meta: {
        type: Array,
        required: true
      }
    },
    components: {
      Multiselect
    },
    watch: {
      meta () {
        if (!this.meta.length) return

        this.ready = true
        _.each(this.fields, (col) => {
          // 1. prepare options
          let u = _.uniqWith(this.meta, (a, b) => a[col] === b[col])
          u = _.sortBy(_.map(u, (uu) => uu[col]))
          u = _.filter(u, (uu) => uu) // discard null / empty value
          this.all[col] = u

          // 2. initialize active option (default to ALL)
          this.active[col] = []
        })
      }
    },
    data () {
      return {
        ready: false,
        fields: CONFIG.filter.fields,
        all: {},
        active_fields: [],
        active: {}
      }
    },
    methods: {
      getAvalFields () {
        return _.difference(this.fields, this.active_fields)
      },
      clickAdd () {
        let inactive_fields = this.getAvalFields()
        if (!inactive_fields.length) return
        this.active_fields.push(inactive_fields[0])
      },
      clickRemove (idx) {
        this.active_fields.splice(idx, 1)
      },
      clickOption (col, d) {
        this.active[col] = d
        let active = this.active

        // probably need closure?
        let filter_func = function (points) {
          return _.filter(points, (p) => {
            let pass = true
            _.each(aval, (c) => {
              if (active[c] !== ALL && p[c] !== active[c]) {
                pass = false
              }
            })

            return pass
          })
        }

        this.$emit('filter', filter_func)
      }
    }
  }
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
