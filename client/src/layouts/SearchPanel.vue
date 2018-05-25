<template>
  <div class="bd-search-panel d-flex flex-column" :style="styles"
       v-click-outside="close">
    <div class="bd-search-panel-top">
      <!--No results-->
      <div v-if="value && !results.length" class="text-muted m-3">
        No results found.
      </div>

      <!--Results-->
      <div v-if="value && results.length" class="mt-2 ml-2 mr-2">
        <div v-for="result in results"
             @mouseover="onHighlight(result, $event)"
             @mouseout="onHighlight()"
             @click="clickResult(result)">
          <list-row :p="result" style="border: 0" hoverColor="#ebdef3"></list-row>
        </div>
      </div>
    </div>

    <!--Count-->
    <div class="pt-1 pb-1 pl-3 bd-search-count d-flex justify-content-between"
         v-if="open && total">
      <div>
        <small>{{total}} results found.</small>
      </div>
      <div v-if="shared.tab === 0">
        <button class="btn btn-link btn-sm" @click="addAll">Add all to group</button>
      </div>
    </div>

    <!--Toolbar-->
    <div class="p-3 bd-border-top" v-if="open">
      <div class="mb-2 d-flex">
        <!--Search By -->
        <b-dropdown dropup size="sm" variant="light"
                    :text="`By ${by}`">
          <b-dropdown-item v-for="b in all_by" @click="by=b" :key="b">
            {{b}}
          </b-dropdown-item>
        </b-dropdown>

        <!--Search In-->
        <b-dropdown dropup size="sm" variant="light"
                    :text="filterText" class="ml-2">
          <b-dropdown-item v-for="f in all_filter" @click="filter=f" :key="f">
            {{f}}
          </b-dropdown-item>
        </b-dropdown>
      </div>

      <!--Input-->
      <div>
        <input class="form-control" :value="value"
               placeholder="Search" v-focus
               @input="updateValue($event.target.value)"/>
      </div>
    </div>
  </div>
</template>

<script>
  import {store, CONFIG} from '../controllers/config'
  import ListRow from './ListRow.vue'
  import _ from 'lodash'

  const MAX = 50
  const ALL = 'All'
  const all_by = CONFIG.search.by
  const col = CONFIG.search.filter

  let timer_handle = null
  let tooltip_handle = null

  export default {
    components: {ListRow},
    name: 'SearchPanel',
    props: {
      open: {
        type: Boolean,
        required: true
      },
      button: {
        required: true
      },
      meta: {
        required: true
      }
    },
    computed: {
      styles () {
        return {
          width: this.open ? '25%' : '0'
        }
      },
      results () {
        // only return the first N elements
        return this.matches.slice(0, MAX)
      },
      total () {
        return this.results.length < MAX ? this.results.length : `More than ${MAX}`
      },
      filterText () {
        let which = this.filter === ALL ? `all ${col}s` : this.filter
        return `In ${which}`
      }
    },
    watch: {
      meta () {
        if (!this.meta.length) return

        let u = _.uniqWith(this.meta, (a, b) => a[col] === b[col])
        u = _.sortBy(_.map(u, (uu) => uu[col]))
        u = _.filter(u, (uu) => uu) // discard null / empty value
        u.push(ALL)
        this.all_filter = u
      },
      by () {
        this.matches = this.computeMatches()
      },
      filter () {
        this.matches = this.computeMatches()
      }
    },
    data() {
      return {
        matches: [],
        by: all_by[0],
        all_by: all_by,
        filter: ALL,
        all_filter: [],
        value: '',
        shared: store.state
      }
    },
    directives: {
      focus: {
        inserted: function (el) {
          el.focus()
        }
      }
    },
    methods: {
      // when user clicks outside the search drawer to close it
      close (event) {
        if (!(event.target === this.button || this.button.contains(event.target))) {
          this.$emit('close')
        }
      },

      // Add result to the selected list
      addOne (p) {
        if (!_.includes(store.selected, p.i)) {
          store.selected.push(p.i)
        }
      },
      addAll () {
        _.each(this.matches, (p) => this.addOne(p))
      },

      // when a result row is clicked
      clickResult (p) {
        if (store.state.tab === 0) {
          // group tab is active, add to group
          this.addOne(p)
        } else {
          // vector tab is active, set selected point
          store.state.clicked_point = p
        }
      },

      // when a result row is hovered
      onHighlight (p, event) {
        if (tooltip_handle) {
          clearTimeout(tooltip_handle)
        }

        if (p && event) {
          tooltip_handle = setTimeout(() => {
            p.clientX = event.clientX
            p.clientY = event.clientY
            store.state.detail = p
          }, 1000)
        } else {
          store.state.detail = p
        }
      },

      // wait a bit until users finish typing a whole word
      scheduleSearch () {
        // cancel previous search request
        if (timer_handle) {
          clearTimeout(timer_handle)
        }

        // if search string is empty, update immediately
        if (!this.value) {
          this.matches = []
          return
        }

        // hack so we don't have "no result" message in the middle
        if (this.value.length === 1) {
          this.matches = this.computeMatches()
          return
        }

        // schedule search
        timer_handle = setTimeout(() => {
          this.matches = this.computeMatches()
        }, 200)
      },

      // really perform the search
      computeMatches () {
        let re = new RegExp(this.value, 'i')
        return  _.filter(this.meta, (p) => {
          if (this.filter !== ALL && p[col] !== this.filter) {
            return false
          }
          return re.test(p[this.by])
        })
      },

      // when user types
      updateValue (value) {
        if (tooltip_handle) {
          clearTimeout(tooltip_handle)
          tooltip_handle = null
        }

        this.value = value
        this.scheduleSearch()
      }
    }
  }
</script>

<style>
  .bd-search-panel {
    position: absolute;
    top: 0;
    left: 0;
    height: 100vh;
    border-right: 1px solid rgba(0,0,0,.1);
    background-color: #fafafa;
    box-shadow: 2px 0 6px rgba(0, 0, 0, .1);
    transition: width .4s;
    z-index: 2000;
  }

  .bd-search-count {
    background-color: #eee;
  }

  .bd-search-panel-top {
    overflow-y: auto;
    height: calc(100vh - 6rem);
  }

  .bd-border-top {
    border-top: 1px solid rgba(0, 0, 0, .1)
  }
</style>
