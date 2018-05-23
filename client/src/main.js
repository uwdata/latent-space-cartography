import Vue from 'vue'
import App from './App.vue'
import VueResource from 'vue-resource'
import BootstrapVue from 'bootstrap-vue'
import router from './router'
import {log_debug} from "./controllers/config"

Vue.use(VueResource)
Vue.use(BootstrapVue)

/**
 * Custom directives
 */
Vue.directive('click-outside', {
  bind: function (el, binding, vnode) {
    el.event = function (event) {
      // click is outside the el and its childrens
      if (!(el === event.target || el.contains(event.target))) {
        // call the method provided by directive attribute
        vnode.context[binding.expression](event);
      }
    };
    document.body.addEventListener('click', el.event)
  },
  unbind: function (el) {
    document.body.removeEventListener('click', el.event)
  },
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
  mounted: function () {
    log_debug('main.js', 'mounted()')
  }
})
