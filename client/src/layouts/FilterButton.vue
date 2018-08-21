<template>
  <div v-if="ready" class="d-inline-block float-right">
    <b-btn :class="{'btn-light': !active_fields.length}"
           v-b-modal.modal-filter v-b-tooltip.hover title="Filter">
      <i class="fa fa-sliders"></i>
    </b-btn>

    <b-modal id="modal-filter" ref="modalFilter" size="lg"
             title="Filter" hide-footer>
      <!--Hint-->
      <div class="m-3 text-muted" v-if="!active_fields.length">
        No active filters.
      </div>

      <!--Drop-downs-->
      <div class="m-3" v-if="active_fields.length" >
        <div class="mb-2 bd-subtitle text-uppercase">Filter By</div>
        <div v-for="(f, idx) in active_fields" class="mb-2 d-flex">
          <div>
            <multiselect v-model="active_fields[idx]" :options="getAvalFields()"
                         :show-labels="false" style="min-width: 150px"></multiselect>
          </div>
          <div class="ml-2">
            <multiselect-wrapper :options="all[f]" v-on:update="onSelectUpdate"
                                 :field="f"></multiselect-wrapper>
          </div>
          <button class="btn btn-link ml-2" @click="clickRemove(f, idx)">
            remove
          </button>
        </div>
      </div>

      <!--Button-->
      <div class="m-3 d-flex justify-content-between">
        <!--Add button-->
        <b-btn class="btn-light btn-lg" v-if="getAvalFields().length"
               @click="clickAdd"
               v-b-tooltip.hover title="Add a Criterion">
          <i class="fa fa-plus"></i>
        </b-btn>

        <!--Apply and Reset-->
        <div v-if="active_fields.length">
          <button class="btn btn-light mr-2" @click="clickReset">Reset</button>
          <button class="btn btn-primary" @click="clickApply">Apply</button>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import Multiselect from 'vue-multiselect'
  import MultiselectWrapper from './MultiselectWrapper.vue'

  export default {
    name: 'FilterButton',
    props: {
      meta: {
        type: Array,
        required: true
      }
    },
    components: {
      MultiselectWrapper,
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
      onSelectUpdate (field, value) {
        this.active[field] = value
      },
      getAvalFields () {
        return _.difference(this.fields, this.active_fields)
      },
      clickAdd () {
        let inactive_fields = this.getAvalFields()
        if (!inactive_fields.length) return
        this.active_fields.push(inactive_fields[0])
      },
      clickRemove (field, idx) {
        this.active_fields.splice(idx, 1)
        this.active[field] = []
      },
      clickReset () {
        this.active_fields = []
        _.each(this.fields, (col) => {
          this.active[col] = []
        })

        this.$emit('filter', _.identity)
        this.$refs.modalFilter.hide()
      },
      clickApply () {
        let active = this.active
        let active_fields = this.active_fields

        // probably need closure?
        let filter_func = function (points) {
          return _.filter(points, (p) => {
            let pass = true
            _.each(active_fields, (f) => {
              let vals = active[f]
              if (vals.length) {
                pass = false
                _.each(vals, (val) => {
                  if (val === p[f]) {
                    pass = true
                  }
                })
              }
            })

            return pass
          })
        }

        this.$emit('filter', filter_func)
        this.$refs.modalFilter.hide()
      }
    }
  }
</script>
