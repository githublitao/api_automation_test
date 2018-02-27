import Login from './views/Login.vue'
import NotFound from './views/404.vue'
import Home from './views/Home.vue'
import Main from './views/Main.vue'
import Monkey from './views/Monkey.vue'
import About from './views/About.vue'
import Project from './views/Project.vue'

let routes = [
    {
        path: '/login',
        component: Login,
        name: '',
        hidden: true
    },
    {
        path: '/404',
        component: NotFound,
        name: '',
        hidden: true
    },
    {
        path: '/',
        component: Home,
        name: '',
        children: [
            { path: '/project', component: Project, iconCls:'el-icon-message', name: '项目列表'},
            { path: '/monkey', component: Monkey, iconCls:'fa fa-id-card-o', name: 'Moneky测试'},
            { path: '/about', component: About, iconCls:'fa fa-address-card', name: '关于我们'},
            ]
    },
    {
        path: '*',
        hidden: true,
        redirect: { path: '/404' }
    }
];

export default routes;