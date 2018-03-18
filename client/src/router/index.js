import Vue from 'vue'
import Router from 'vue-router'
import MainPage from '../pages/MainPage.vue'
import ScatterCanvasPage from '../pages/ScatterCanvasPage.vue'
import ScatterSvgPage from '../pages/ScatterSvgPage.vue'
import ScatterPage from '../pages/ScatterPage.vue'
import TsnePage from '../pages/TsnePage.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: MainPage
    },
    {
      path: '/scatter_canvas',
      name: 'scatter_canvas',
      component: ScatterCanvasPage
    },
    {
      path: '/scatter_svg',
      name: 'scatter_svg',
      component: ScatterSvgPage
    },
    {
      path: '/pca',
      name: 'pca',
      component: ScatterPage
    },
    {
      path: '/tsne',
      name: 'tsne',
      component: TsnePage
    }
  ]
})
