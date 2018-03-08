import Vue from 'vue'
import Router from 'vue-router'
import MainPage from '../pages/MainPage.vue'
import ScatterCanvasPage from '../pages/ScatterCanvasPage.vue'
import ScatterSvgPage from '../pages/ScatterSvgPage.vue'

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
      name: 'scatter',
      component: ScatterCanvasPage
    },
    {
      path: '/scatter_svg',
      name: 'scatter',
      component: ScatterSvgPage
    }
  ]
})
