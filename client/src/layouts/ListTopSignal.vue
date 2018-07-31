<template>
  <div>
    <div class="bd-subtitle mb-3 text-uppercase">
      Largest in {{start ? 'Start' : 'End'}} Group
    </div>
    <div>
      <div v-for="signal in signals" class="d-flex">
        <div class="mr-3 text-right w-25" style="font-size: 0.7em;">{{signal.gene}}</div>
        <div class="w-75 d-flex align-items-center">
          <div class="bd-bar" :class="{'start': start, 'end': !start}"
               :style="{width: signal.width + '%'}"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'ListTopSignal',
    props: {
      signals: {
        required: true
      },
      start: {
        required: true
      }
    },
    data() {
      return {
      }
    },
    methods: {
    }
  }
</script>

<style>
  .bd-bar {
    height: 4px;
  }

  .bd-bar.start{
    background-color: rgba(131,88,213, 0.6);
  }

  .bd-bar.end{
    background-color: rgba(244,196,76, 0.6);
  }
</style>
