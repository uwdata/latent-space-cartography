<template>
  <div v-if="ready" class="d-inline-block float-right">
    <b-dropdown v-for="col in cols" :text="getText(col)"
                variant="light" class="ml-2">
      <div class="d-none">{{redraw}}</div>
      <b-dropdown-item v-for="d in all[col]" @click="clickOption(col, d)" :key="d">
        {{d}}
      </b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
  import {DATASET} from '../controllers/config'
  import _ from 'lodash'

  const aval = DATASET === 'emoji' ? ['category', 'platform'] : []
  const ALL = 'All'

  export default {
    name: 'FilterDropdown',
    props: {
      meta: {
        type: Array,
        required: true
      }
    },
    watch: {
      meta () {
        if (!this.meta.length) return

        this.ready = true
        _.each(aval, (col) => {
          // 1. prepare options
          let u = _.uniqWith(this.meta, (a, b) => a[col] === b[col])
          u = _.sortBy(_.map(u, (uu) => uu[col]))
          u = _.filter(u, (uu) => uu) // discard null / empty value
          u.push(ALL)
          this.all[col] = u

          // 2. initialize active option (default to ALL)
          this.active[col] = ALL
        })
      }
    },
    data () {
      return {
        redraw: 0,
        ready: false,
        cols: aval,
        all: {},
        active: {}
      }
    },
    methods: {
      getText (col) {
        return `${_.startCase(col)}: ${this.active[col]}`
      },
      clickOption (col, d) {
        this.redraw++
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
