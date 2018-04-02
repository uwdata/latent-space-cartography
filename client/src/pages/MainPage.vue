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
          {link: '/tsne', name: 't-SNE'},
          {link: '/splom', name: 'PCA - Scatter Plots Matrix'},
          {link: '/analogy', name: 'Analogy'},
          {link: '/pca', name: 'PCA - 2 Dimensions'},
          {link: '/scatter_canvas', name: 'Scatter Plot in Canvas'},
          {link: '/scatter_svg', name: 'Scatter Plot in SVG'}
        ]
      }
    }
  }
</script>
