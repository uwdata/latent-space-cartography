<template>
  <div class="bd-search-panel d-flex flex-column" :style="styles"
       v-click-outside="close">
    <div class="h-100">
      {{value}}
    </div>
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

  const all_by = ['name', 'codepoints', 'shortcode']

  export default {
    name: 'SearchPanel',
    props: {
      open: {
        type: Boolean,
        required: true
      },
      button: {
        required: true
      }
    },
    computed: {
      styles () {
        return {
          width: this.open ? '25%' : '0'
        }
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

  .bd-border-top {
    border-top: 1px solid rgba(0, 0, 0, .1)
  }
</style>
