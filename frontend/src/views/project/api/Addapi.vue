<template>
    <section>
        <el-button class="return-list el-icon-d-arrow-left">接口列表</el-button>
            <el-form :model="form" ref="form" :rules="FormRules">
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="接口分组:" label-width="72px">
                            <el-select v-model="form.request4" prop="request4" placeholder="请求方式">
                                <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="4" >
                        <el-form-item>
                            <el-select v-model="form.Http4" placeholder="HTTP协议">
                            <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :gutter="10">
                    <el-col :span='8'>
                        <el-form-item label="接口名称:" label-width="72px">
                            <el-input v-model="form.addr" placeholder="名称" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="10">
                        <el-form-item label="状态:" label-width="72px">
                            <el-select v-model="form.request4" prop="request4" placeholder="请求方式">
                                <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="URL:" label-width="72px">
                            <el-select v-model="form.request4" prop="request4" placeholder="请求方式">
                                <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="2">
                        <el-form-item>
                            <el-select v-model="form.Http4" placeholder="HTTP协议">
                            <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span='18'>
                        <el-form-item>
                            <el-input v-model="form.addr" placeholder="地址" clearable></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :span="24">
                    <el-collapse v-model="activeNames" @change="handleChange">
                        <el-collapse-item title="请求头部" name="1">
                            <template>
                                <el-checkbox-group v-model="checkHeadList">
                                    <div class="head-class">
                                        <el-row :gutter="10">
                                            <el-col :span="1">
                                            <span>头部</span>
                                            </el-col>
                                            <el-col :span="4">
                                            <span>标签</span>
                                            </el-col>
                                            <el-col :span="15">
                                            <span>内容</span>
                                            </el-col>
                                            <el-col :span="4">
                                            </el-col>
                                        </el-row>
                                    </div>
                                    <el-row :gutter="10">
                                        <el-col :span="1" style="margin-top:6px">
                                        <el-checkbox></el-checkbox>
                                        </el-col>
                                        <el-col :span="4">
                                        <el-form-item>
                                            <el-select v-model="header4" placeholder="head标签" filterable>
                                            <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                            </el-select>
                                        </el-form-item>
                                        </el-col>
                                        <el-col :span="15">
                                        <el-form-item>
                                            <el-input placeholder="内容" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                        <el-col :span="4">
                                            <i class="el-icon-delete" style="font-size:30px"></i>
                                        </el-col>
                                    </el-row>
                                </el-checkbox-group>
                            </template>
                        </el-collapse-item>
                        <el-collapse-item title="请求参数" name="2">
                            <div>
                                <el-row :span="24">
                                    <el-col :span="4"><el-radio v-model="radio" label="1">表单(form-data)</el-radio></el-col>
                                    <el-col :span="4"><el-radio v-model="radio" label="2">源数据(raw)</el-radio></el-col>
                                    <el-col :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterTyep">表单转源数据</el-checkbox></el-col>
                                </el-row>
                            </div>
                            <template>
                                <div :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                                <el-checkbox-group v-model="checkParameterList">
                                    <div class="head-class">
                                        <el-row :gutter="10">
                                            <el-col :span="1">
                                                <span>头部</span>
                                            </el-col>
                                            <el-col :span="4">
                                                <span>参数名</span>
                                            </el-col>
                                            <el-col :span="7">
                                                <span>参数值</span>
                                            </el-col>
                                            <el-col :span="9">
                                                <span>参数说明</span>
                                            </el-col>
                                            <el-col :span="3">
                                            </el-col>
                                    </el-row>
                                    </div>
                                    <el-row :gutter="10">
                                        <el-col :span="1" style="margin-top:6px">
                                        <el-checkbox></el-checkbox>
                                        </el-col>
                                        <el-col :span="4">
                                        <el-form-item>
                                            <el-input placeholder="参数名" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                        <el-col :span="7">
                                        <el-form-item>
                                            <el-input placeholder="参数值" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                         <el-col :span="8">
                                        <el-form-item>
                                            <el-input placeholder="参数说明" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                        <el-col :span="2">
                                            <el-button>更多设置</el-button>
                                        </el-col>
                                        <el-col :span="2">
                                        <i class="el-icon-delete" style="font-size:30px"></i>
                                        </el-col>
                                    </el-row>
                                </el-checkbox-group>
                            </div>
                        </template>
                         <template>
                             <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model="textarea"></el-input>
                         </template>
                    </el-collapse-item>
                    <el-collapse-item title="返回参数" name="3">
                        <template>
                            <div :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                            <el-checkbox-group v-model="checkParameterList">
                                <div class="head-class">
                                    <el-row :gutter="10">
                                        <el-col :span="1">
                                            <span>头部</span>
                                        </el-col>
                                        <el-col :span="4">
                                            <span>参数名</span>
                                        </el-col>
                                        <el-col :span="7">
                                            <span>参数值</span>
                                        </el-col>
                                        <el-col :span="9">
                                            <span>参数说明</span>
                                        </el-col>
                                        <el-col :span="3">
                                        </el-col>
                                    </el-row>
                                    </div>
                                    <el-row :gutter="10">
                                        <el-col :span="1" style="margin-top:6px">
                                        <el-checkbox></el-checkbox>
                                        </el-col>
                                        <el-col :span="4">
                                        <el-form-item>
                                            <el-input placeholder="参数名" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                        <el-col :span="7">
                                        <el-form-item>
                                            <el-input placeholder="参数值" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                         <el-col :span="8">
                                        <el-form-item>
                                            <el-input placeholder="参数说明" clearable></el-input>
                                        </el-form-item>
                                        </el-col>
                                        <el-col :span="2">
                                            <el-button>更多设置</el-button>
                                        </el-col>
                                        <el-col :span="2">
                                        <i class="el-icon-delete" style="font-size:30px"></i>
                                        </el-col>
                                    </el-row>
                                </el-checkbox-group>
                            </div>
                        </template>
                         <template>
                             <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model="textarea"></el-input>
                         </template>
                    </el-collapse-item>
                    <el-collapse-item title="响应结果" name="4">
                        <div style="margin-bottom: 10px">
                            <el-button @click="showData">Body</el-button>
                            <el-button @click="showHead">Head</el-button>
                            <el-button type="primary">格式转换</el-button>
                        </div>
                        <el-card class="box-card">
                          <div slot="header" class="clearfix">
                            <span>200</span>
                          </div >
                            <div v-show="result">{"code":"999999","msg":"成功","data":{"first_name":"李涛","last_name":"","phone":"18202886999","email":"daf@qq.com","key":"312b599e490d6d2ac20fbe66353d56f0de856180","date_joined":"2018-03-05 09:49:00"}}</div>
                            <div v-show="!result">{"code":"999999","msg":"成功","data":{"first_name":"321","last_name":"","phone":"18202886999","email</div>
                        </el-card>
                    </el-collapse-item>
                </el-collapse>
                </el-row>
            </el-form>
    </section>
</template>
<script>
  export default {
    data() {
      return {
        request: [{value: 'get', label: 'GET'},
                    {value: 'post', label: 'POST'},
                    {value: 'put', label: 'PUT'},
                    {value: 'delete', label: 'DELETE'}],
        Http: [{value: 'http', label: 'HTTP'},
                {value: 'https', label: 'HTTPS'}],
        checkHeadList: [],
        checkParameterList: [],
        ParameterTyep: true,
        textarea: '',
        header: [{value: 'Accept', label: 'Accept'},
                    {value: 'Accept-Charset', label: 'Accept-Charset'},
                    {value: 'Accept-Encoding', label: 'Accept-Encoding'},
                    {value: 'Accept-Language', label: 'Accept-Language'},
                    {value: 'Accept-Ranges', label: 'Accept-Ranges'},
                    {value: 'Authorization', label: 'Authorization'},
                    {value: 'Cache-Control', label: 'Cache-Control'},
                    {value: 'Connection', label: 'Connection'},
                    {value: 'Cookie', label: 'Cookie'},
                    {value: 'Content-Length', label: 'Content-Length'},
                    {value: 'Content-Type', label: 'Content-Type'},
                    {value: 'Content-MD5', label: 'Content-MD5'},
                    {value: 'Date', label: 'Date'},
                    {value: 'Expect', label: 'Expect'},
                    {value: 'From', label: 'From'},
                    {value: 'Host', label: 'Host'},
                    {value: 'If-Match', label: 'If-Match'},
                    {value: 'If-Modified-Since', label: 'If-Modified-Since'},
                    {value: 'If-None-Match', label: 'If-None-Match'},
                    {value: 'If-Range', label: 'If-Range'},
                    {value: 'If-Unmodified-Since', label: 'If-Unmodified-Since'},
                    {value: 'Max-Forwards', label: 'Max-Forwards'},
                    {value: 'Origin', label: 'Origin'},
                    {value: 'Pragma', label: 'Pragma'},
                    {value: 'Proxy-Authorization', label: 'Proxy-Authorization'},
                    {value: 'Range', label: 'Range'},
                    {value: 'Referer', label: 'Referer'},
                    {value: 'TE', label: 'TE'},
                    {value: 'Upgrade', label: 'Upgrade'},
                    {value: 'User-Agent', label: 'User-Agent'},
                    {value: 'Via', label: 'Via'},
                    {value: 'Warning', label: 'Warning'}],
        header4: "",
        radio: "",
        radioType: "",
        result: true,
        activeNames: ['1', '2', '3', '4'],
        FormRules: {
            request4: [{required: true, message: '请输入名称', trigger: 'blur'}]
        },
        form: {
            request4: 'GET',
            Http4: 'HTTP',
            addr: '',
        }
      }
    },
    methods: {
        changeParameterType() {
            console.log(this.radio)
            if (this.radio === '1') {
                this.ParameterTyep = !this.ParameterTyep
            } else {
                this.ParameterTyep = !this.ParameterTyep
            }
        },
        showData() {
            this.result = true
        },
        showHead(){
            this.result = false
        },
        handleChange(val) {
      },
      onSubmit() {
        console.log('submit!');
      }
    },
    watch: {
        radio() {
            this.changeParameterType()
        }
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
        margin: 10px;
    }
    .parameter-b {
        display: none;
    }
</style>
