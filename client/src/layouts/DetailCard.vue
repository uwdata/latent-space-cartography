<template>
  <div class="card mb-3" v-if="detail && necessary">
    <div class="card-header d-flex justify-content-between">
      <div>Details</div>
      <div class="pl-3 bd-pointer" @click="clickClose()">
        <span>
          <i class="fa fa-fw fa-times text-muted"></i>
        </span>
      </div>
    </div>
    <div class="card-body">
      <div class="d-flex" style="font-size: 0.8em;">
        <!--Image-->
        <div class="p1" v-if="data_type === 'image'">
          <img :src="imageUrl(detail)" />
        </div>
        <!--Special formatting for emoji dataset-->
        <div class="w-100 ml-2" v-if="dataset==='emoji'">
          <div class="mb-1 d-flex justify-content-between">
            <div>
              <b>{{detail.name}}</b>
              <small class="ml-1 text-muted" v-if="detail.shortcode">
                {{detail.shortcode}}
              </small>
            </div>
            <div v-if="detail.category">
              <span class="badge" :style="badgeStyle(detail.category)">
                {{detail.category}}
              </span>
            </div>
          </div>
          <div class="mb-1" v-if="detail.platform">
            {{detail.platform}} {{detail.version}}
          </div>
          <div class="mb-1 text-muted" v-if="detail.codepoints">
            <small>Code Points: {{detail.codepoints}}</small>
          </div>
        </div>
        <!--Generic formatting-->
        <div class="w-100 ml-2" v-else>
          <div class="mb-1">
            <b>{{detail.name}}</b>
          </div>
          <!--The heatmap-->
          <div v-if="data_type === 'other'" class="mt-3" id="heatmap-container">
          </div>
          <div class="mb-1" v-for="field in fields" v-if="detail[field]">
            <b>{{fieldName(field)}}:</b>
            {{detail[field]}}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import {store, CONFIG} from '../controllers/config'
  import _ from 'lodash'
  import Heatmap from '../controllers/analogy/heatmap'

  export default {
    name: 'DetailCard',
    data () {
      return {
        shared: store.state,
        dataset: CONFIG.dataset,
        data_type: CONFIG.data_type,
        chart: new Heatmap()
      }
    },
    computed: {
      fields () {
        let fields = CONFIG.schema.meta
        return _.filter(fields, (f) => f !== 'i' && f !== 'name' && f !== 'mean_color')
      },
      necessary () {
        return CONFIG.schema.meta.length > 2
      },
      detail () {
        if (this.shared.detail_card) {
          store.getRaw(this.shared.detail_card.i)
            .then((data) => {
              this.chart.setData(data)
              this.chart.draw('#heatmap-container')
            }, () => {})
        }
        return this.shared.detail_card
      }
    },
    methods: {
      clickClose () {
        this.shared.detail_card = null
      },
      // helper
      badgeStyle (category) {
        let darkText = {
          'Smileys & People': true
        }
        let bg = {
          'Symbols': '#4c78a8',
          'Objects': '#72b7b2',
          'Flags': '#e45756',
          'Smileys & People': '#eeca3b',
          'Travel & Places': '#b279a2',
          'Animals & Nature': '#54a24b',
          'Food & Drink': '#f58518',
          'Activity': '#ff9da6'
        }

        let styles = {
          backgroundColor: bg[category] || '#bab0ac'
        }

        if (!darkText[category]) {
          styles['color'] = '#fff'
        }

        return styles
      },
      imageUrl (p) {
        return store.getImageUrl(p.i)
      },
      fieldName (f) {
        return _.map(f.split('_'), (word) => _.capitalize(word)).join(' ')
      }
    }
  }
</script>
