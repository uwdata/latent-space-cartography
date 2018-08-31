<template>
  <div>
    <div v-for = "word in list" class="d-flex">
      <div class="d-flex align-items-center bd-bar-container"
           :class="{compact: compact}">
        <div :style="{width: (word.distance * 100) + '%'}"
             :class="{muted: word.muted}"
             class="bd-bar-thick">{{word.distance.toFixed(3)}}</div>
      </div>
      <div :class="{compact: compact}"
           class="bd-word text-truncate">{{word.name}}</div>
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
      compact: {
        'default': false
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

  .bd-bar-thick.muted{
    background-color: #ddd !important;
  }

  .bd-bar-container {
    width: 25%;
  }

  .bd-bar-container.compact {
    width: 40% !important;
  }

  .bd-word {
    font-size: 12px;
    margin-left: 1rem;
    width: 75%;
  }

  .bd-word.compact {
    width: 60% !important;
    margin-left: .25rem !important;
  }
</style>
