<template>
  <div class="dropdown">
    <input class="form-control" :value="value"
           placeholder="Search ..."
           @input="updateValue($event.target.value)"
           @keydown.enter = 'enter'
           @keydown.down = 'down'
           @keydown.up = 'up'>
    <div class="dropdown-menu" style="width:100%" :class="{'show': openSuggestion}">
      <a class="dropdown-item text-truncate"
         v-for="(val, index) in matches" href="#"
         :class="{'active': isActive(index)}"
         @click="suggestionClick(index)">
        {{ val.name }}
      </a>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash'

  export default {
    name: 'auto-complete',
    props: {
      value: {
        type: String,
        required: true
      },
      points: {
        type: Array,
        required: true
      },
      attribute: {
        type: String,
        'default': 'name'
      }
    },
    data () {
      return {
        open: false,
        current: 0
      }
    },
    computed: {
      // Filtering the suggestion based on the input
      matches () {
        if (!this.value) return []
        let re = new RegExp(this.value, 'i')
        let res = _.filter(this.points, (p) => re.test(p[this.attribute]))
        // only return the first 10 elements
        return res.slice(0, 10)
      },

      openSuggestion () {
        return this.value !== '' &&
          this.matches.length !== 0 &&
          this.open === true
      }
    },
    methods: {
      // Triggered the input event to cascade the updates to
      // parent component
      updateValue (value) {
        if (this.open === false) {
          this.open = true
          this.current = 0
        }
        this.$emit('input', value)
      },

      // When enter key pressed on the input
      enter () {
        this.$emit('input', this.matches[this.current][this.attribute])
        this.open = false
      },

      // When up arrow pressed while suggestions are open
      up () {
        if (this.current > 0) {
          this.current--
        }
      },

      // When down arrow pressed while suggestions are open
      down () {
        if (this.current < this.matches.length - 1) {
          this.current++
        }
      },

      // For highlighting element
      isActive (index) {
        return index === this.current
      },

      // When one of the suggestion is clicked
      suggestionClick (index) {
        this.$emit('input', this.matches[index][this.attribute])
        this.open = false
      }
    }
  }
</script>
