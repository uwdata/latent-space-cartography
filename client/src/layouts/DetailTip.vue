<template>
  <div class="bd-detail p-2" v-if="detail" v-bind:style="styles">
    <div class="d-flex" style="font-size: 0.8em;">
      <div class="p1" v-if="show_image">
        <img :src="imageUrl(detail)" />
      </div>
      <div class="w-100 ml-2">
        <!--Special formatting for emoji dataset-->
        <div v-if="dataset==='emoji'">
          <div class="mb-1 d-flex justify-content-between">
            <div>
              <b>{{detail.name}}</b>
              <small class="ml-1 text-muted" v-if="detail.shortcode">
                {{detail.shortcode}}
              </small>
            </div>
            <div>
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

        <!--Generic case-->
        <div v-else>
          <div class="mb-1">
            <b>{{detail.name}}</b>
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
  import _ from 'lodash'
  import {store, CONFIG} from '../controllers/config'

  export default {
    name: 'DetailTip',
    data () {
      return {
        shared: store.state,
        dataset: CONFIG.dataset,
        show_image: CONFIG.data_type === 'image'
      }
    },
    computed: {
      fields () {
        let fields = CONFIG.schema.meta
        return _.filter(fields, (f) => f !== 'i' && f !== 'name' && f !== 'mean_color')
      },
      detail () {
        return this.shared.detail
      },
      x () {
        if (!this.detail || !this.detail.clientX) {
          return 0
        }

        let x = Math.max(0, this.detail.clientX)
        return x + 'px'
      },
      y () {
        if (!this.detail || !this.detail.clientY) {
          return 0
        }

        let y = Math.max(0, this.detail.clientY + 15)
        return y + 'px'
      },
      styles () {
        return {
          top: this.y,
          left: this.x
        }
      },
    },
    methods: {
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

<style>
  .bd-detail {
    width: 240px;
    background-color: #fff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    position: absolute;
    z-index: 15000;
    line-height: 1.2em;
  }
</style>
