import Vue from 'vue'
import App from './App.vue'
import VueResource from 'vue-resource'
import BootstrapVue from 'bootstrap-vue'
import router from './router'
import {log_debug, setConfig} from "./controllers/config"
import http from 'axios'

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

/**
 * Load config file from server before initializing
 */
http.post('/api/load_config', {})
  .then((response) => {
    let msg = response.data

    if (msg) {
      setConfig(msg.config)

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
    }
  }, () => {})
