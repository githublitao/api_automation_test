<template>
    <section>
        <router-link :to="{ name: '用例接口列表', params: {project_id: this.$route.params.project_id,case_id: this.$route.params.case_id}}" style='text-decoration: none;color: aliceblue;'>
            <el-button class="return-list"><i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回列表</el-button>
        </router-link>
        <router-link :to="{ name: '用例接口列表', params: {project_id: this.$route.params.project_id,case_id: this.$route.params.case_id}}" style='text-decoration: none;color: aliceblue;'>
            <el-button class="return-list" style="float: right">取消</el-button>
        </router-link>
        <el-button class="return-list" type="primary" style="float: right; margin-right: 15px" @click.native="addApi">保存</el-button>
        <el-form :model="form" ref="form" :rules="FormRules">
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
                <el-form-item label="接口名称:" label-width="83px" prop="name">
                    <el-input v-model.trim="form.name" placeholder="名称" auto-complete></el-input>
                </el-form-item>
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="URL:" label-width="83px">
                            <el-select v-model="form.request4"  placeholder="请求方式" @change="checkRequest">
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
                        <el-form-item prop="addr">
                            <el-input v-model.trim="form.addr" placeholder="地址" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row>
                            <el-table-column prop="name" label="标签" min-width="28%" sortable>
                                <template slot-scope="scope">
                                    <el-select placeholder="head标签" filterable v-model="scope.row.name" style="width: 90%">
                                        <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                    </el-select>
                                    <el-input class="selectInput" v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入内容"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="内容" min-width="40%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="interrelate" label="是否关联" min-width="13%" sortable>
                                <template slot-scope="scope">
                                    <el-switch v-model="scope.row.interrelate">
                                    </el-switch>
                                </template>
                            </el-table-column>
                            <el-table-column min-width="7%">
                                <template slot-scope="scope">
                                    <el-button type="primary" size="mini" style="margin-bottom: 5px" v-if="scope.row.interrelate" @click="handleCorrelation(scope.$index, scope.row)">关联</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="7%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delHead(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="5%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.head.length-1)" size="mini" class="el-icon-plus" @click="addHead"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-collapse-item>
                    <el-collapse-item title="请求参数" name="2">
                        <div style="margin: 5px">
                            <el-row :span="24">
                                <el-col :span="4"><el-radio v-model="radio" label="form-data">表单(form-data)</el-radio></el-col>
                                <el-col v-if="request3" :span="4"><el-radio v-model="radio" label="raw">源数据(raw)</el-radio></el-col>
                                <el-col v-if="request3" :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterTyep">表单转源数据</el-checkbox></el-col>
                            </el-row>
                        </div>
                        <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
                            <el-table-column prop="name" label="参数名" min-width="28%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="40%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                                </template>
                            </el-table-column>
                            <el-table-column prop="interrelate" label="是否关联" min-width="13%" sortable>
                                <template slot-scope="scope">
                                    <el-switch v-model="scope.row.interrelate">
                                    </el-switch>
                                </template>
                            </el-table-column>
                            <el-table-column min-width="7%">
                                <template slot-scope="scope">
                                    <el-button type="primary" size="mini" style="margin-bottom: 5px" v-if="scope.row.interrelate" @click="handleCorrelation(scope.$index, scope.row)">关联</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="7%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delParameter(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="5%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <template>
                            <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model.trim="form.parameterRaw"></el-input>
                        </template>
                    </el-collapse-item>
                    <el-dialog title="关联" :visible.sync="searchApiVisible" :close-on-click-modal="false">
                        <el-row :gutter="10">
                            <el-col :span="6">
                                <div style="height:400px;line-height:100px;overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6">
                                    <el-menu default-active="2" class="el-menu-vertical-demo" active-text-color="rgb(32, 160, 255)" :unique-opened="true">
                                        <el-menu-item v-for="(item,index) in ApiList" :index="index+''" :key="item.id" @click.native="handleResponse(index)">{{item.name}}</el-menu-item>
                                    </el-menu>
                                </div>
                            </el-col>
                            <el-col :span="18">
                                <div style="height:400px;line-height:100px;overflow:auto;overflow-x:hidden;">
                                    <el-table :data="ApiResponse" highlight-current-row v-loading="apiResponseLoading" @current-change="handleCurrentChange"
                                              style="width: 100%;" :show-header="false" height="400" max-height="400" @selection-change="selsChange">
                                        <el-table-column prop="name" label="名称" min-width="100%" sortable>
                                        </el-table-column>
                                    </el-table>
                                </div>
                            </el-col>
                        </el-row>
                        <div slot="footer" class="dialog-footer">
                            <el-button @click.native="searchApiVisible = false">取消</el-button>
                            <el-button type="primary" @click.native="addInterrelateSubmit" :loading="saveCorrelation">保存</el-button>
                        </div>
                    </el-dialog>
                    <el-collapse-item title="测试结果校验" name="3">
                        <el-card class="box-card">
                            <div slot="header" class="clearfix">
                                <el-radio-group v-model="form.check">
                                    <el-radio-button label="no_check"><div>不校验</div></el-radio-button>
                                    <el-radio-button label="only_check_status"><div>校验http状态</div></el-radio-button>
                                    <el-radio-button label="json"><div>JSON校验</div></el-radio-button>
                                    <el-radio-button label="entirely_check"><div>完全校验</div></el-radio-button>
                                    <el-radio-button label="Regular_check"><div>正则校验</div></el-radio-button>
                                </el-radio-group>
                                <el-input v-if="form.check==='Regular_check'"
                                          style="width: 10%;padding-left: 5px;margin-top: 1px"
                                          v-modele="form.RegularParam"
                                          placeholder="请输入绑定参数名"
                                >
                                </el-input>
                            </div>
                            <div v-show="showCheck">
                                <el-select v-model="form.checkHttp" placeholder="HTTP状态">
                                    <el-option v-for="(item,index) in httpCode" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                                <el-input style="margin-top: 10px" v-model.trim="form.checkData" type="textarea" :rows="8" placeholder="请输入mock内容"></el-input>
                            </div>
                        </el-card>
                    </el-collapse-item>
                </el-collapse>
            </el-row>
        </el-form>
    </section>
</template>
<script>
    import { test } from '../../../api/api'
    import $ from 'jquery'
    export default {
        data() {
            return {
                request: [{value: 'GET', label: 'GET'},
                    {value: 'POST', label: 'POST'},
                    {value: 'PUT', label: 'PUT'},
                    {value: 'DELETE', label: 'DELETE'}],
                Http: [{value: 'HTTP', label: 'HTTP'},
                    {value: 'HTTPS', label: 'HTTPS'}],
                ParameterTyep: true,
                radio: "form-data",
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
                httpCode:[{value: '200', label: '200'},
                    {value: '404', label: '404'},
                    {value: '400', label: '400'},
                    {value: '500', label: '500'},
                    {value: '502', label: '502'},
                    {value: '302', label: '302'}],
                radioType: "",
                result: true,
                activeNames: ['1', '2', '3'],
                id: "",
                searchApiVisible: false,
                ApiList: [],
                ApiResponse: [],
                apiResponseLoading: false,
                saveCorrelation: false,
                showCheck: false,
                sels: [],//列表选中列
                interrelateObjects: "",
                request3:true,
                form: {
                    name: '',
                    request4: 'POST',
                    Http4: 'HTTP',
                    addr: '',
                    head: [{name: "", value: "", interrelate:0,},
                        {name: "", value: "", interrelate:0,}],
                    parameterRaw: "",
                    parameter: [{name: "", value: "", interrelate:0,},
                        {name: "", value: "", interrelate:0}],
                    parameterType: "",
                    check: "no_check",
                    RegularParam: "",
                    checkHttp: "",
                    checkData: "",
                },
                FormRules: {
                    name : [{ required: true, message: '请输入名称', trigger: 'blur' }],
                    addr : [{ required: true, message: '请输入地址', trigger: 'blur' }],
                },
            }
        },
        methods: {
            checkRequest(){
                let request = this.form.request4;
                if (request==="GET" || request==="DELETE"){
                    this.request3=false
                } else {
                    this.request3=true
                }
            },
            handleCurrentChange(val) {
                this.currentRow = val;
            },
            selsChange(sels){
                this.sels = sels;
            },
            handleCorrelation(index, row) {
                let self = this;
                $.ajax({
                    type: "get",
                    url: test+"/api/automation/get_correlation_response",
                    async: true,
                    data: {project_id: this.$route.params.project_id,
                        case_id: this.$route.params.case_id,
                    },
                    headers: {
                        Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        if (data.code === '999999') {
                            if (data.data.length) {
                                self.ApiList = [];
                                data.data.forEach((item) => {
                                    self.ApiList.push(item)
                                });
                                self.searchApiVisible = true;
                                // self.handleResponse(index);
                                self.interrelateObjects = row
                            } else {
                                self.$message.warning({
                                    message: '无前置接口',
                                    center: true,
                                });
                            }
                        }
                        else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            });
                        }
                    },
                });
            },
            handleResponse(index) {
                this.ApiResponse = [];
                this.ApiList[index].response.forEach((item) =>{
                    this.ApiResponse.push(item)
                })
            },
            addInterrelateSubmit() {
                this.saveCorrelation = true;
                try {
                    this.interrelateObjects['value'] =  this.currentRow['tier'];
                } catch (e) {
                    this.$message.warning({
                        message: '未选中接口参数',
                        center: true,
                    });
                }
                this.interrelateObjects['interrelate'] = true;
                this.saveCorrelation = false;
                this.searchApiVisible = false;
            },
            addApi: function () {
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        let self = this;
                        let formatRaw = false;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.form.parameterType = self.radio;
                            let _type = self.form.parameterType;
                            let _parameter = {};
                            if ( _type === 'form-data') {
                                // if ( self.radioType === true) {
                                //     _type = 'raw';
                                //     self.form.parameter.forEach((item) => {
                                //         _parameter[item.name] = item.value
                                //     });
                                // } else {
                                //     _parameter = self.form.parameter;
                                // }
                                 if ( self.radioType === true) {
                                    formatRaw = true;
                                }
                                _parameter = self.form.parameter;

                            } else {
                                _parameter = self.form.parameterRaw
                            }
                            let param = JSON.stringify({
                                project_id: Number(self.$route.params.project_id),
                                automationTestCase_id: Number(self.$route.params.case_id),
                                name: self.form.name,
                                httpType: self.form.Http4,
                                requestType: self.form.request4,
                                apiAddress: self.form.addr,
                                headDict: self.form.head,
                                requestParameterType: _type,
                                formatRaw: formatRaw,
                                requestList: _parameter,
                                examineType: self.form.check,
                                RegularParam: self.form.RegularParam,
                                httpCode: self.form.checkHttp,
                                responseData: self.form.checkData.toString()
                            });
                            $.ajax({
                                type: "post",
                                url: test+"/api/automation/add_new_api",
                                async: true,
                                data: param,
                                headers: {
                                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                                },
                                timeout: 5000,
                                success: function(data) {
                                    if (data.code === '999999') {
                                        self.$router.push({ name: '用例接口列表', params: { project_id: self.$route.params.project_id, case_id: self.$route.params.case_id}});
                                        self.$message({
                                            message: '保存成功',
                                            center: true,
                                            type: 'success'
                                        })
                                    }
                                    else {
                                        self.$message.error({
                                            message: data.msg,
                                            center: true,
                                        })
                                    }
                                },
                            })
                        })
                    }
                })
            },
            addHead() {
                let headers = {name: "", value: "", interrelate:0,};
                this.form.head.push(headers)
            },
            delHead(index) {
                this.form.head.splice(index, 1);
                if (this.form.head.length === 0) {
                    this.form.head.push({name: "", value: "", interrelate:0,})
                }
            },
            addParameter() {
                let headers = {name: "", value: "", interrelate:0,};
                this.form.parameter.push(headers)
            },
            delParameter(index) {
                this.form.parameter.splice(index, 1);
                if (this.form.parameter.length === 0) {
                    this.form.parameter.push({name: "", value: "", interrelate:0,})
                }
            },
            changeParameterType() {
                if (this.radio === 'form-data') {
                    this.ParameterTyep = true
                } else {
                    this.ParameterTyep = false
                }
            },
            handleChange(val) {
            },
        },
        watch: {
            radio() {
                this.changeParameterType()
            },
            form: {
                //注意：当观察的数据为对象或数组时，curVal和oldVal是相等的，因为这两个形参指向的是同一个数据对象
                handler(curVal,oldVal){
                    if (curVal.check === 'no_check') {
                        this.showCheck = false
                    } else {
                        this.showCheck = true
                    }
                },
                deep:true
            },
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
        position: absolute;
        /*margin-left: 7px;*/
        padding-left: 9px;
        width: 180px;
        /*border-radius:0px;*/
        /*height: 38px;*/
        left: 1px;
        border-right: 0px;
    }
</style>
<style lang="scss">
    .selectInput{
        input{
            border-right: 0px;
            border-radius: 4px 0px 0px 4px;
        }
    }
</style>
