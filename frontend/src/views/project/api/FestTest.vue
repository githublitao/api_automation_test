<template>
    <section>
        <el-button class="return-list el-icon-d-arrow-left">接口列表</el-button>
            <el-form :model="form" ref="form" :rules="FormRules">
                <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="接口分组:" label-width="83px">
                            <el-select v-model="form.firstGroup" prop="request4" placeholder="父分组" @change="changeSecondGroup">
                                <el-option v-for="(item,index) in group" :key="index+''" :label="item.name" :value="index"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="4" >
                        <el-form-item>
                            <el-select v-model="form.secondGroup" placeholder="子分组">
                                <el-option v-for="(item,index) in secondGroup" :key="index+''" :label="item.name" :value="item.name"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :gutter="10">
                    <el-col :span='8'>
                        <el-form-item v-model="form.name" label="接口名称:" label-width="83px" prop="name">
                            <el-input placeholder="名称" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span="10">
                        <el-form-item label="状态:" label-width="72px">
                            <el-select v-model="form.status" prop="request4" placeholder="接口状态">
                                <el-option v-for="(item,index) in status" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="URL:" label-width="83px" prop="url">
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
                        <el-form-item v-model="form.addr" prop="url">
                            <el-input placeholder="地址" clearable></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>
                </div>
                <el-row :span="24">
                    <el-collapse v-model="activeNames" @change="handleChange">
                        <el-collapse-item title="请求头部" name="1">
                            <el-table :data="form.head" highlight-current-row>
                                <el-table-column type="selection" min-width="5%" label="头部">
                                </el-table-column>
                                <el-table-column prop="name" label="标签" min-width="15%" sortable>
                                    <template slot-scope="scope">
                                       <el-select placeholder="head标签" filterable v-model="scope.row.name">
                                           <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                       </el-select>
                                   </template>
                                </el-table-column>
                                <el-table-column prop="value" label="内容" min-width="50%" sortable>
                                    <template slot-scope="scope">
                                       <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                                   </template>
                                </el-table-column>
                                <el-table-column label="操作" min-width="5%">
                                    <template slot-scope="scope">
                                        <i class="el-icon-delete" style="font-size:30px" @click="delHead(scope.$index)"></i>
                                    </template>
                                </el-table-column>
                                <el-table-column label="" min-width="10%">
                                    <template slot-scope="scope">
                                        <el-button v-if="scope.$index===(form.head.length-1)" size="mini" class="el-icon-plus" @click="addHead"></el-button>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </el-collapse-item>
                        <el-collapse-item title="请求参数" name="2">
                            <div>
                                <el-row :span="24">
                                    <el-col :span="4"><el-radio v-model="radio" label="1">表单(form-data)</el-radio></el-col>
                                    <el-col :span="4"><el-radio v-model="radio" label="2">源数据(raw)</el-radio></el-col>
                                    <el-col :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterTyep">表单转源数据</el-checkbox></el-col>
                                </el-row>
                            </div>
                            <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                                <el-table-column type="selection" min-width="5%" label="头部">
                                </el-table-column>
                                <el-table-column prop="name" label="参数名" min-width="15%" sortable>
                                    <template slot-scope="scope">
                                       <el-input v-model="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                                   </template>
                                </el-table-column>
                                <el-table-column prop="value" label="参数值" min-width="25%" sortable>
                                    <template slot-scope="scope">
                                       <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                                   </template>
                                </el-table-column>
                                <el-table-column prop="desc" label="参数说明" min-width="25%" sortable>
                                    <template slot-scope="scope">
                                       <el-input v-model="scope.row.desc" :value="scope.row.desc" placeholder="请输入参数说明"></el-input>
                                   </template>
                                </el-table-column>
                                <el-table-column label="操作" min-width="8%">
                                    <template slot-scope="scope">
                                        <i class="el-icon-delete" style="font-size:30px" @click="delParameter(scope.$index)"></i>
                                        <el-button type="primary" size="mini" style="margin-bottom: 5px">更多设置</el-button>
                                    </template>
                                </el-table-column>
                                <el-table-column label="" min-width="5%">
                                    <template slot-scope="scope">
                                        <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                    </template>
                                </el-table-column>
                            </el-table>
                         <template>
                             <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model="textarea"></el-input>
                         </template>
                    </el-collapse-item>
                    <el-collapse-item title="返回参数" name="3">
                        <el-table :data="form.response" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
                            <el-table-column prop="name" label="参数名" min-width="15%" sortable>
                                <template slot-scope="scope">
                                        <el-input v-model="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="25%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column prop="desc" label="参数说明" min-width="25%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.desc" :value="scope.row.desc" placeholder="请输入参数说明"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="8%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px" @click="delResponse(scope.$index)"></i>
                                    <el-button type="primary" size="mini" style="margin-bottom: 5px">更多设置</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="5%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.response.length-1)" size="mini" class="el-icon-plus" @click="addResponse"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-collapse-item>
                    <el-collapse-item title="普通mock" name="4">
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
        group: [{id:1, name: '分组1', secondGroup:[{id:1, name: '321'}]},
        {id:2, name: '分组2', secondGroup:[{id:1, name: '321'}]},],
        secondGroup: [],
        status: [{value: true, label: '启用'},
                    {value: false, label: '禁用'}],
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
        form: {
            firstGroup: '',
            secondGroup: '',
            name: '',
            status: true,
            request4: 'GET',
            Http4: 'HTTP',
            addr: '',
            head: [{name: "", value: ""},
            {name: "", value: ""}],
            parameter: [{name: "", value: "", desc: ""},
            {name: "", value: "", desc: ""}],
            response: [{name: "", value: "", desc: ""},
            {name: "", value: "", desc: ""}],
        },
        FormRules: {
            name : [{ required: true, message: '请输入名称', trigger: 'blur' }],
            url : [{ required: true, message: '请输入地址', trigger: 'blur' }],
        }
      }
    },
    methods: {
        addHead() {
            var headers = {name: "", value: ""}
            this.form.head.push(headers)
        },
        delHead(index) {
            if (this.form.head.length !== 1) {
                this.form.head.splice(index, 1)
            }
        },
        addParameter() {
            var headers = {name: "", value: ""}
            this.form.parameter.push(headers)
        },
        delParameter(index) {
            if (this.form.parameter.length !== 1) {
                this.form.parameter.splice(index, 1)
            }
        },
        addResponse() {
            var headers = {name: "", value: ""}
            this.form.response.push(headers)
        },
        delResponse(index) {
            if (this.form.response.length !== 1) {
                this.form.response.splice(index, 1)
            }
        },
        changeSecondGroup(val) {
            console.log(this.group[val].secondGroup)
            this.secondGroup = this.group[val].secondGroup
        },
        handleDel: function (index, row) {
           console.log(index,row.name, row.value)
        },
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
