<template>
  <div>
    <h3>Go to ...</h3>
    <ul>
      <li v-for="row in menus">
        <router-link :to="row.link">
          <span>{{ row.name }}</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'MainPage',
    data() {
      return {
        menus: [
          {link: '/scatter', name: 'PCA - Scatter Plot'},
          {link: '/scatter_canvas', name: 'Scatter Plot in Canvas'},
          {link: '/scatter_svg', name: 'Scatter Plot in SVG'}
        ]
      }
    }
  }
</script>
