import NotFound from './views/common/404.vue'
import Login from './views/common/Login.vue'
import Home from './views/common/Home.vue'
import Monkey from './views/Monkey.vue'
import About from './views/About.vue'
import Project from './views/project/Project.vue'
import ProjectInfo from './views/project/ProjectInfo.vue'
import Globalhost from './views/project/Globalhost.vue'
import API from './views/project/API.vue'
import AutomationTest from './views/project/AutomationTest.vue'
import ProjectMember from './views/project/ProjectMember.vue'
import ProjectDynamic from './views/project/ProjectDynamic.vue'

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
//  {
//      path: '*',
//      hidden: true,
//      projectHidden: true,
//      redirect: { path: '/404' }
//  },    
    {
        path: '/projectInfo/:project_id',
        component: ProjectInfo,
        name: '项目',
        hidden: true,
        children: [
            { path: '/projectInfo/:project_id', component: ProjectInfo, name: '项目概况', leaf: true},
            { path: '/Globalhost/:project_id', 
              component: Globalhost, 
              name: '全局配置',
              children: [
                    { path: '/Globalhost/:project_id', component: Globalhost, name: 'host配置'},
                    { path: '/404/:project_id', component: NotFound,  name: '自定义方法'},
              ]
            },
            { path: '/api/:project_id', component: API, name: 'API接口', leaf: true},
            { path: '/automationTest/:project_id', component: AutomationTest, name: '自动化测试', leaf: true},
            { path: '/projectMember/:project_id', component: ProjectMember, name: '成员管理', leaf: true},
            { path: '/projectDynamic/:project_id', component: ProjectDynamic, name: '项目动态', leaf: true},
            ]
    },
//  {
//      path: '/Globalhost',
//      component: ProjectInfo,
//      name: '全局配置',
//      hidden: true,
//      children: [
//          { path: '/Globalhost', component: Globalhost,  name: 'host配置'},
//          { path: '/404', component: NotFound,  name: '自定义方法'},
//          ]
//  },
//  {
//      path: '/api',
//      component: API,
//      name: 'API接口',
//      hidden: true,
//      leaf: true  // 没有节点
//  },
//  {
//      path: '/automationTest',
//      component: AutomationTest,
//      name: '自动化测试',
//      hidden: true,
//      leaf: true  // 没有节点
//  },
//  {
//      path: '/projectMember',
//      component: ProjectMember,
//      name: '成员管理',
//      hidden: true,
//      leaf: true  // 没有节点
//  },
//  {
//      path: '/projectDynamic',
//      component: ProjectDynamic,
//      name: '项目动态',
//      hidden: true,
//      leaf: true  // 没有节点
//  },
];

export default routes;