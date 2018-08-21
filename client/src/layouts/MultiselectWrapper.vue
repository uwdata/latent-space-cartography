<template>
  <multiselect v-model="value" :options="options" :multiple="true"
               :close-on-select="false" :preserve-search="true"
               :show-labels="false" @input="onUpdate"
               :hide-selected="true" :placeholder="hint">
  </multiselect>
</template>

<script>
  import Multiselect from 'vue-multiselect'

  export default {
    name: 'MultiselectWrapper',
    props: {
      options: {
        type: Array,
        required: true
      },
      field: {
        type: String,
        required: true
      },
      hint: {
        type: String,
        'default': 'Type to search ...'
      }
    },
    components: {
      Multiselect
    },
    data () {
      return {
        value: []
      }
    },
    methods: {
      onUpdate () {
        this.$emit('update', this.field, this.value)
      }
    }
  }
</script>
