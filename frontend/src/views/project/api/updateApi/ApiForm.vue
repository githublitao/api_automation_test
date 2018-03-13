<template>
    <section>
        <router-link :to="{ name: '接口列表', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                <el-button class="return-list el-icon-d-arrow-left">接口列表</el-button>
        </router-link>
            <el-radio-group v-model="radio3">
              <el-radio-button label="基础信息"></el-radio-button>
              <el-radio-button label="测试"></el-radio-button>
              <el-radio-button label="历史"></el-radio-button>
              <el-radio-button label="修改"></el-radio-button>
              <el-radio-button label="删除"></el-radio-button>
            </el-radio-group>
    </section>
</template>

<script>
    export default {
        name: "api-form",
        data() {
            return {
                radio3: "基础信息",
            }
            },
        mounted() {
            console.log(this.$route.params.project_id);
            console.log(this.$route.params.api_id)

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