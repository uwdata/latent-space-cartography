<template>
  <div class="card mb-3" v-if="detail_point">
    <div class="card-header">Details</div>
    <div class="card-body">
      <p>{{detail_point.name}}</p>
      <div class="d-flex" style="font-size: 0.8em;">
        <div class="p1">
          <img :src="imageUrl(detail_point)" />
        </div>
        <div class="w-100 ml-2">
          <div class="mb-2">
            <b>Industry: </b>
            {{detail_point.industry}}
          </div>
          <div class="mb-2">
            <b>Data Source: </b>
            {{detail_point.source}}
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
      detail_point: {
        required: true
      }
    },
    methods: {
      // helper
      imageUrl (p) {
        return store.getImageUrl(p.i)
      }
    }
  }
</script>
