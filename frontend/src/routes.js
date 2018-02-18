import NotFound from './views/common/404.vue'
import Login from './views/Login.vue'
import Home from './views/Home.vue'
import Monkey from './views/Monkey.vue'
import About from './views/About.vue'
import Project from './views/Project.vue'
import ProjectInfo from './views/projectInfo.vue'

let routes = [
    {
        path: '/login',
        component: Login,
        name: '',
        hidden: true,
        projectHidden: true
    },
    {
        path: '/404',
        component: NotFound,
        name: '',
        hidden: true,
        projectHidden: true
    },
    {
        path: '/',
        component: Home,
        name: '',
        projectHidden: true,
        children: [
            { path: '/project', component: Project, iconCls:'el-icon-message', name: '项目列表'},
            { path: '/monkey', component: Monkey, iconCls:'fa fa-id-card-o', name: 'Moneky测试'},
            { path: '/about', component: About, iconCls:'fa fa-address-card', name: '关于我们'},
            ]
    },
    {
        path: '*',
        hidden: true,
        projectHidden: true,
        redirect: { path: '/404' }
    },    
    {
        path: '/projectInfo',
        component: ProjectInfo,
        name: '项目概况',
        hidden: true,
        leaf: true  // 没有节点
    },
    {
        path: '/projectInfo',
        component: ProjectInfo,
        name: '全局配置',
        hidden: true,
        children: [
            { path: '/project', component: Project,  name: 'host配置'},
            { path: '/monkey', component: Monkey,  name: '自定义方法'},
            ]
    },
    {
        path: '/projectInfo',
        component: ProjectInfo,
        name: 'API接口',
        hidden: true,
        leaf: true  // 没有节点
    },
    {
        path: '/projectInfo',
        component: ProjectInfo,
        name: '自动化测试',
        hidden: true,
        leaf: true  // 没有节点
    },
    {
        path: '/projectInfo',
        component: ProjectInfo,
        name: '成员管理',
        hidden: true,
        leaf: true  // 没有节点
    },
    {
        path: '/projectInfo',
        component: ProjectInfo,
        name: '项目动态',
        hidden: true,
        leaf: true  // 没有节点
    },
];

export default routes;