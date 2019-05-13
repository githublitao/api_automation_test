import axios from 'axios';

// export const test = 'http://127.0.0.1:8000';
export const test = 'http://120.79.232.23:8000';
// 登录
export const requestLogin = params => { return axios.post(`${test}/api/user/login`, params).then(res => res.data); };
// 记录访客
export const recordVisitor = params => { return axios.post(`${test}/api/user/VisitorRecord`, params).then(res => res.data); };
// 获取项目
export const getProject = (headers, params) => {
    return axios.get(`${test}/api/project/project_list`, { params: params, headers:headers}).then(res => res.data); };
// 删除项目
export const delProject = (headers, params) => {
    return axios.post(`${test}/api/project/del_project`, params, {headers}).then(res => res.data); };
// 禁用项目
export const disableProject = (headers, params) => {
    return axios.post(`${test}/api/project/disable_project`, params, {headers}).then(res => res.data); };
// 启用项目
export const enableProject = (headers, params) => {
    return axios.post(`${test}/api/project/enable_project`, params, {headers}).then(res => res.data); };
// 修改项目
export const updateProject = (headers, params) => {
    return axios.post(`${test}/api/project/update_project`, params, {headers}).then(res => res.data); };
// 添加项目
export const addProject = (headers, params) => {
    return axios.post(`${test}/api/project/add_project`, params, {headers}).then(res => res.data); };
// 获取项目详情
export const getProjectDetail = (headers, params) => {
    return axios.get(`${test}/api/title/project_info`, { params: params, headers:headers}).then(res => res.data); };
// 获取测试地址列表
export const getHost = (headers, params) => {
    return axios.get(`${test}/api/global/host_total`, { params: params, headers:headers}).then(res => res.data); };
// 删除测试地址列表
export const delHost = (headers, params) => {
    return axios.post(`${test}/api/global/del_host`, params, {headers}).then(res => res.data); };
// 禁用测试地址列表
export const disableHost = (headers, params) => {
    return axios.post(`${test}/api/global/disable_host`, params, {headers}).then(res => res.data); };
// 启用测试地址列表
export const enableHost = (headers, params) => {
    return axios.post(`${test}/api/global/enable_host`, params, {headers}).then(res => res.data); };
// 修改测试地址列表
export const updateHost = (headers, params) => {
    return axios.post(`${test}/api/global/update_host`, params, {headers}).then(res => res.data); };
// 添加测试地址列表
export const addHost = (headers, params) => {
    return axios.post(`${test}/api/global/add_host`, params, {headers}).then(res => res.data); };
// 获取项目动态
export const getProjectDynamicList = (headers, params) => {
    return axios.get(`${test}/api/dynamic/dynamic`, { params: params, headers:headers}).then(res => res.data); };
// 获取项目成员
export const getProjectMemberList = (headers, params) => {
    return axios.get(`${test}/api/member/project_member`, { params: params, headers:headers}).then(res => res.data); };
// 获取发送邮件配置
export const getEmailConfigDetail = (headers, params) => {
    return axios.get(`${test}/api/member/get_email`, { params: params, headers:headers}).then(res => res.data); };
// 删除邮件配置
export const delEmailConfig = (headers, params) => {
    return axios.post(`${test}/api/member/del_email`, params, {headers}).then(res => res.data); };
// 添加邮件配置
export const addEmailConfig = (headers, params) => {
    return axios.post(`${test}/api/member/email_config`, params, {headers}).then(res => res.data); };
// 获取自动化测试结果
export const getTestResultList = (headers, params) => {
    return axios.get(`${test}/api/report/auto_test_report`, { params: params, headers:headers}).then(res => res.data); };
// 获取最近10次测试时间
export const getTestTenTime = (headers, params) => {
    return axios.get(`${test}/api/report/test_time`, { params: params, headers:headers}).then(res => res.data); };
// 获取最近10次测试比例结果
export const getTestTenResult = (headers, params) => {
    return axios.get(`${test}/api/report/lately_ten`, { params: params, headers:headers}).then(res => res.data); };
// 添加接口
export const addApiDetail = (headers, params) => {
    return axios.post(`${test}/api/api/add_api`, params, {headers}).then(res => res.data); };
// 获取接口分组列表
export const getApiGroupList = (headers, params) => {
    return axios.get(`${test}/api/api/group`, { params: params, headers:headers}).then(res => res.data); };
// 添加接口分组
export const addApiGroup = (headers, params) => { return axios.post(`${test}/api/api/add_group`, params, {headers}).then(res => res.data); };
// 修改接口分组
export const updateApiGroup = (headers, params) => {
    return axios.post(`${test}/api/api/update_name_group`, params, {headers}).then(res => res.data); };
// 删除接口分组
export const delApiGroup = (headers, params) => {
    return axios.post(`${test}/api/api/del_group`, params, {headers}).then(res => res.data); };
