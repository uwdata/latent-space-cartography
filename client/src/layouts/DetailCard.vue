<template>
  <div class="card mb-3" v-if="detail">
    <div class="card-header">Details</div>
    <div class="card-body">
      <div class="d-flex" style="font-size: 0.8em;">
        <div class="p1">
          <img :src="imageUrl(detail)" />
        </div>
        <div class="w-100 ml-2">
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
          <div class="mb-1" v-if="detail.industry">
            <b>Industry: </b>
            {{detail.industry}}
          </div>
          <div class="mb-1" v-if="detail.source">
            <b>Data Source: </b>
            {{detail.source}}
          </div>
          <div class="mb-1" v-if="detail.platform">
            {{detail.platform}} {{detail.version}}
          </div>
          <div class="mb-1 text-muted" v-if="detail.codepoints">
            <small>Code Points: {{detail.codepoints}}</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import {store} from '../controllers/config'

  export default {
    name: 'DetailCard',
    props: {
      detail: {
        required: true
      }
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
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>
