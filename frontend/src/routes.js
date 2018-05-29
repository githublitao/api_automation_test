import NotFound from './views/common/404.vue'
import Login from './views/common/Login.vue'
import Home from './views/Home.vue'
import robot from './views/robot/robot.vue'
import About from './views/About.vue'
import projectList from './views/Projectlist.vue'
import ProjectInfo from './views/project.vue'
import globalHost from './views/project/global/Globalhost.vue'
import API from './views/project/api/API.vue'
import ApiList from './views/project/api/ApiList.vue'
import ApiListGroup from './views/project/api/ApiListGroup.vue'
import FestTest from './views/project/api/FestTest.vue'
import addApi from './views/project/api/Addapi.vue'
import detail from './views/project/api/updateApi/ApiForm.vue'
import ApiInfo from './views/project/api/updateApi/ApiInfo.vue'
import testApi from './views/project/api/updateApi/TestApi.vue'
import UpdateApi from './views/project/api/updateApi/UpdateApi.vue'
import ApiDynamic from './views/project/api/updateApi/ApiDynamic.vue'
import AutomationTest from './views/project/automation/AutomationTest.vue'
import CaseList from './views/project/automation/CaseList.vue'
import CaseListGroup from './views/project/automation/CaseListGroup.vue'
import CaseApiList from './views/project/automation/CaseApiList.vue'
import AddCaseApi from './views/project/automation/AddCaseApi.vue'
import UpdateCaseApi from './views/project/automation/UpdateCaseApi.vue'
import TestReport from './views/project/automation/TestReport.vue'
import ProjectMember from './views/project/ProjectMember.vue'
import ProjectDynamic from './views/project/ProjectDynamic.vue'
import ProjectTitle from './views/project/projectTitle/ProjectTitle.vue'
import ProjectReport from './views/project/projectReport'

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
            { path: '/projectList', component: projectList, iconCls:'el-icon-message', name: '项目列表'},
            { path: '/robot', component: robot, iconCls:'fa fa-id-card-o', name: '消息机器人'},
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
        path: '/project/project=:project_id',
        component: ProjectInfo,
        name: '项目',
        hidden: true,
        children: [
            {   path: '/ProjectTitle/project=:project_id', component: ProjectTitle, name: '项目概况', leaf: true},
            {   path: '/GlobalHost/project=:project_id', component: globalHost, name: 'Host配置', leaf: true},
            {   path: '/api/project=:project_id',
                    component: API,
                    name: 'API接口',
                    leaf: true,
                    child: true,
                    children: [
                        {   path: '/apiList/project=:project_id', component: ApiList, name: '接口列表'},
                        {   path: '/apiList/project=:project_id/first=:firstGroup/seconde=:secondGroup', component: ApiListGroup, name: '分组接口列表'},
                        {   path: '/fastTest/project=:project_id', component: FestTest, name: '快速测试'},
                        {   path: '/addApi/project=:project_id', component: addApi, name: '新增接口'},
                        {   path: '/detail/project=:project_id/api=:api_id',
                            component: detail,
                            name: '接口',
                            children: [
                                { path: '/apiInfo/project=:project_id/api=:api_id', component: ApiInfo, name: '基础信息'},
                                { path: '/testApi/project=:project_id/api=:api_id', component: testApi, name: '测试'},
                                { path: '/apiDynamic/project=:project_id/api=:api_id', component: ApiDynamic, name: '历史'},
                            ]
                        },
                        { path: '/updateApi/project=:project_id/api=:api_id', component: UpdateApi, name: '修改'},
                    ]},
            {   path: '/automationTest/project=:project_id',
                    component: AutomationTest,
                    name: '自动化测试',
                    leaf: true,
                    child: true,
                    children: [
                        {   path: '/caseList/project=:project_id', component: CaseList, name: '用例列表'},
                        {   path: '/caseList/project=:project_id/first=:firstGroup/second=:secondGroup', component: CaseListGroup, name: '分组用例列表'},
                        {   path: '/caseApiList/project=:project_id/case=:case_id', component: CaseApiList, name: '用例接口列表'},
                        {   path: '/addCaseApi/project=:project_id/case=:case_id', component: AddCaseApi, name: '添加新接口'},
                        {   path: '/updateCaseApi/project=:project_id/case=:case_id/api=:api_id', component: UpdateCaseApi, name: '修改接口'},
                        {   path: '/testReport/project=:project_id', component: TestReport, name: '测试报告'},
                    ]
            },
            {   path: '/projectMember/project=:project_id', component: ProjectMember, name: '成员管理', leaf: true},
            {   path: '/projectDynamic/project=:project_id', component: ProjectDynamic, name: '项目动态', leaf: true},
            {   path: '/projectReport/project=:project_id', component: ProjectReport, name: '自动化测试报告', leaf: true},
            ]
    },
];

export default routes;