<template>
    <section>
        <router-link :to="{ name: '接口列表', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                <el-button class="return-list el-icon-d-arrow-left">接口列表</el-button>
        </router-link>
        <el-radio-group v-model="radio3" style="margin-left: 50px">
            <router-link :to="{ name: '基础信息', params: { project_id: this.$route.params.project_id, api_id: this.$route.params.api_id}}" style='text-decoration:none;'>
                <el-radio-button label="基础信息">
                        <div style="width: 80px">基础信息</div>
                </el-radio-button>
            </router-link>
            <router-link :to="{ name: '测试', params: { project_id: this.$route.params.project_id, api_id: this.$route.params.api_id}}" style='text-decoration:none;'>
                <el-radio-button label="测试">
                        <div style="width: 80px">测试</div>
                </el-radio-button>
            </router-link>
            <router-link :to="{ name: '基础信息', params: { project_id: this.$route.params.project_id, api_id: this.$route.params.api_id}}" style='text-decoration:none;'>
                <el-radio-button label="历史">
                        <div style="width: 80px">历史</div>
                </el-radio-button>
            </router-link>
            <router-link :to="{ name: '基础信息', params: { project_id: this.$route.params.project_id, api_id: this.$route.params.api_id}}" style='text-decoration:none;'>
                <el-radio-button label="修改">
                        <div style="width: 80px">修改</div>
                </el-radio-button>
            </router-link>
            <router-link :to="{ name: '基础信息', params: { project_id: this.$route.params.project_id, api_id: this.$route.params.api_id}}" style='text-decoration:none;'>
                <el-radio-button label="删除">
                        <div style="width: 80px">删除</div>
                </el-radio-button>
            </router-link>
        </el-radio-group>
        <div style="margin-left: 10px;margin-right: 20px">
            <router-view></router-view>
        </div>
    </section>
</template>

<script>
    export default {
        name: "api-form",
        data() {
            return {
                radio3: "",
            }
            },
        mounted() {

        }
    }

</script>

<style lang="scss" scoped>
 .return-list {
    margin-top: 0px;
    margin-bottom: 10px;
    border-radius: 25px;
 }
 .head-class {
     font-size: 17px
 }
    .parameter-a {
        display: block;
    }
    .parameter-b {
        display: none;
    }
    .selectInput {
        position:absolute;
        margin-left:7px;
        padding-left:10px;
        width:5%;
        height:25px;
        left:1px;
        top:1px;
        border-bottom:0px;
        border-right:0px;
        border-left:0px;
        border-top:0px;
    }
</style>