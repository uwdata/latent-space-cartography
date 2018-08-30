<template>
  <div>
    <div class="bd-subtitle text-uppercase mb-3" v-if="title">{{title}}</div>
    <div v-for = "word in list" class="d-flex">
      <div class="w-25 d-flex align-items-center">
        <div :style="{width: (word.distance * 100) + '%'}"
             class="bd-bar-thick">{{word.distance.toFixed(3)}}</div>
      </div>
      <div class="ml-3 w-75 bd-word">{{word.name}}</div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'ListKnn',
    props: {
      list: {
        required: true
      },
      title: {
        'default': null
      }
    }
  }
</script>

<style>
  .bd-bar-thick {
    height: 14px;
    background-color: rgba(244,196,76, 0.8);
    font-size: 8px;
    line-height: 8px;
    padding: 2px 5px;
    margin-bottom: 1px;
  }

  .bd-word {
    font-size: 12px;
  }
</style>
