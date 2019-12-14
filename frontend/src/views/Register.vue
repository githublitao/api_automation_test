<template>
    <p class="page-container">扫描登录中...</p>
</template>

<script>
    import {dingLogin} from "../api/api";

    export default {
        name: "Register",
        methods: {
            DingDingLogin(){
                let data = {
                    code: this.$route.query.code
                };
                dingLogin(data).then(_data => {
                    let _this = this;
                    let {msg, code, data} = _data;
                    if (code === '999999') {
                        sessionStorage.setItem('username', JSON.stringify(data.first_name));
                        sessionStorage.setItem('token', JSON.stringify(data.key));
                        if (_this.$route.query.url) {
                            _this.$router.push(_this.$route.query.url);
                        } else {
                            _this.$router.push('/projectList');
                        }
                    }
                    else {
                         _this.$router.push('/login');
                        _this.$message.error({
                            message: msg,
                            center: true
                        })
                    }
                })
            }
        },
        mounted() {
            this.DingDingLogin()
        }
    }
</script>

<style scoped>
    .page-container {
        font-size: 50px;
        text-align: center;
        color: rgb(192, 204, 218);
    }
</style>