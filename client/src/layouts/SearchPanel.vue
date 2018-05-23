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
        <list-row v-for="result in results" :p="result" style="border: 0"></list-row>
      </div>
    </div>

    <!--Count-->
    <div class="pt-1 pb-1 pl-3 bd-search-count" v-if="open && total">
      <small>{{total}} results found.</small>
    </div>

    <!--Toolbar-->
    <div class="p-3 bd-border-top" v-if="open">
      <div class="mb-2 d-flex">
        <b-dropdown dropup size="sm" variant="light"
                    :text="`By ${by}`">
          <b-dropdown-item v-for="b in all_by" @click="by=b" :key="b">
            {{b}}
          </b-dropdown-item>
        </b-dropdown>
        <b-dropdown dropup size="sm" variant="light"
                    :text="`In all platforms`" class="ml-2">
          <b-dropdown-item v-for="b in all_by" @click="by=b" :key="b">
            {{b}}
          </b-dropdown-item>
        </b-dropdown>
      </div>
      <div>
        <input class="form-control" :value="value"
               placeholder="Search" v-focus
               @input="updateValue($event.target.value)"/>
      </div>
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'
  import ListRow from './ListRow.vue'
  import _ from 'lodash'

  const MAX = 50
  const all_by = ['name', 'codepoints', 'shortcode']

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
      matches () {
        if (!this.value) return []
        let re = new RegExp(this.value, 'i')
        return _.filter(this.meta, (p) => re.test(p[this.by]))
      },
      results () {
        // only return the first N elements
        return this.matches.slice(0, MAX)
      },
      total () {
        return this.results.length < MAX ? this.results.length : `More than ${MAX}`
      }
    },
    data() {
      return {
        by: all_by[0],
        all_by: all_by,
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
      close (event) {
        if (!(event.target === this.button || this.button.contains(event.target))) {
          this.$emit('close')
        }
      },
      updateValue (value) {
        this.value = value
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
