// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import locale from 'element-ui/lib/locale/lang/en'
import VueRouter from 'vue-router'
import routes from './routes'

Vue.use(ElementUI, { locale })
Vue.use(ElementUI)
Vue.use(VueRouter)

Vue.config.productionTip = false

const router = new VueRouter({
  routes
})

router.beforeEach((to, from, next) => {
  // NProgress.start();
  if (to.path === '/login') {
    sessionStorage.removeItem('token')
  }
  let token = JSON.parse(sessionStorage.getItem('token'))
  if (!token && to.path !== '/login') {
    next({ path: '/login' })
  } else {
    next()
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
