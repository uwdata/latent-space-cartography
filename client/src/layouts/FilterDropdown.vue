<template>
  <div v-if="ready" class="d-inline-block float-right">
    <b-dropdown v-for="col in cols" :text="getText(col)" :key="col"
                variant="light" class="ml-2">
      <div class="d-none">{{redraw}}</div>
      <b-dropdown-item v-for="d in all[col]" @click="clickOption(col, d)" :key="d">
        {{d}}
      </b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
  import {CONFIG} from '../controllers/config'
  import _ from 'lodash'

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
        _.each(this.cols, (col) => {
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
        cols: CONFIG.dataset === 'emoji' ? ['category', 'platform'] : [],
        all: {},
        active: {}
      }
    },
    methods: {
      getText (col) {
        let prefix = this.active[col] === ALL ? `${_.startCase(col)}: ` : ''
        return `${prefix}${this.active[col]}`
      },
      clickOption (col, d) {
        this.redraw++
        this.active[col] = d
        let active = this.active
        let cols = this.cols

        // probably need closure?
        let filter_func = function (points) {
          return _.filter(points, (p) => {
            let pass = true
            _.each(cols, (c) => {
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
