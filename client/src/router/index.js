import Vue from 'vue'
import Router from 'vue-router'
import MainPage from '../pages/MainPage.vue'
import ScatterCanvasPage from '../pages/ScatterCanvasPage.vue'
import ScatterSvgPage from '../pages/ScatterSvgPage.vue'
import ScatterPage from '../pages/ScatterPage.vue'
import TsnePage from '../pages/TsnePage.vue'
import SplomPage from '../pages/SplomPage.vue'
import AnalogyPage from '../pages/AnalogyPage.vue'
import ComparePage from '../pages/ComparePage.vue'
import InitialPage from '../pages/InitialPage.vue'

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
    },
    {
      path: '/splom',
      name: 'splom',
      component: SplomPage
    },
    {
      path: '/compare',
      name: 'compare',
      component: ComparePage
    },
    {
      path: '/initial',
      name: 'initial',
      component: InitialPage
    },
    {
      path: '/analogy',
      name: 'analogy',
      component: AnalogyPage
    }
  ]
})
