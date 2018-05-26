<template>
  <div class="chart-btn-group pt-3 pr-3">
    <div class="btn-group-vertical btn-group-sm">
      <b-btn class="btn btn-outline-primary chart-btn"
             :class="{active: brush}"
             @click="toggleBrush"
             id="btn-brush">
        <i class="fa fa-fw fa-sticky-note-o"></i>
      </b-btn>
      <b-btn class="btn btn-outline-warning chart-btn"
             id="btn-night"
             :class="{active: night}"
             @click="toggleBackground">
        <i class="fa fa-fw fa-moon-o"></i>
      </b-btn>
    </div>
    <br>
    <div class="btn-group-vertical btn-group-sm mt-3">
      <b-btn class="btn btn-outline-secondary chart-btn"
             id="btn-zoomin"
             @click="zoomIn">
        <i class="fa fa-fw fa-plus"></i>
      </b-btn>
      <b-btn class="btn btn-outline-secondary chart-btn"
             id="btn-zoomout"
             @click="zoomOut">
        <i class="fa fa-fw fa-minus"></i>
      </b-btn>
      <b-btn class="btn btn-outline-secondary chart-btn"
             id="btn-reset"
             @click="resetZoom">
        <i class="fa fa-fw fa-crosshairs"></i>
      </b-btn>
    </div>

    <b-tooltip target="btn-night" title="Toggle Background Color"
               placement="left"></b-tooltip>
    <b-tooltip target="btn-zoomin" title="Zoom In"
               placement="left"></b-tooltip>
    <b-tooltip target="btn-zoomout" title="Zoom Out"
               placement="left"></b-tooltip>
    <b-tooltip target="btn-reset" title="Reset View"
               placement="left"></b-tooltip>
    <b-tooltip target="btn-brush" title="Toggle Brush"
               placement="left"></b-tooltip>
  </div>
</template>

<script>
  export default {
    name: 'ChartButtons',
    props: {
      chart: {
        type: Object,
        required: true
      }
    },
    data () {
      return {
        night: false,
        brush: false
      }
    },
    methods: {
      toggleBackground () {
        this.night = !this.night
        this.chart.toggleBackground(this.night ? '#000' : '#fff')
      },
      toggleBrush () {
        this.brush = !this.brush
        this.chart.toggleBrushing(this.brush)
      },
      zoomIn () {
        this.chart.zoomView(1.5)
      },
      zoomOut () {
        this.chart.zoomView(0.7)
      },
      resetZoom () {
        this.$emit('reset')
      }
    }
  }
</script>

<style>
  .chart-btn-group {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 1000;
  }

  .chart-btn-group .btn-group-sm {
    background-color: #fff;
    border-radius: 3px;
  }

  .chart-btn {
    color: #8c858d;
    border-color: #8c858d;
  }
</style>
