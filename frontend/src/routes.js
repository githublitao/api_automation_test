import Login from './views/Login.vue'
import Home from './views/Home.vue'

let routes = [
  {
    path: '/login',
    component: Login,
    name: '',
    hidden: true
  },
  {
    path: '/home',
    component: Home,
    name: '',
    hidden: true
  }
]

export default routes
