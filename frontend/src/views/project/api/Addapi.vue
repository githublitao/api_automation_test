<template>
    <section>
        <router-link :to="{ name: '接口列表', params: {project_id: this.$route.params.project_id}}" style='text-decoration: none;color: aliceblue;'>
                <el-button class="return-list el-icon-d-arrow-left">接口列表</el-button>
            </router-link>
        <!--<el-button class="return-list el-icon-d-arrow-left" @click="back">接口列表</el-button>-->
        <el-button class="return-list" style="float: right" @click="back">取消</el-button>
        <el-button class="return-list" type="primary" style="float: right; margin-right: 15px" @click.native="addApi">保存</el-button>
        <el-form :model="form" ref="form" :rules="FormRules">
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
            <el-row :gutter="10">
                <el-col :span="6">
                    <el-form-item label="接口分组:" label-width="83px" prop="firstGroup">
                        <el-select v-model="form.firstGroup" placeholder="父分组" @change="changeSecondGroup">
                            <el-option v-for="(item,index) in group" :key="index+''" :label="item.name" :value="item.id"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="4">
                    <el-form-item prop="secondGroup">
                        <el-select v-model="form.secondGroup" placeholder="子分组">
                            <el-option v-for="(item,index) in secondGroup" :key="index+''" :label="item.name" :value="item.id"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-row :gutter="10">
                <el-col :span='8'>
                    <el-form-item label="接口名称:" label-width="83px" prop="name">
                        <el-input v-model="form.name" placeholder="名称" auto-complete></el-input>
                    </el-form-item>
                </el-col>
                <el-col :span="10">
                    <el-form-item label="状态:" label-width="72px">
                        <el-select v-model="form.status" placeholder="接口状态">
                            <el-option v-for="(item,index) in status" :key="index+''" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-row :gutter="10">
                <el-col :span="4">
                    <el-form-item label="URL:" label-width="83px">
                        <el-select v-model="form.request4"  placeholder="请求方式">
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
                        <el-input v-model="form.addr" placeholder="地址" auto-complete></el-input>
                    </el-form-item>
                </el-col>
            </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row>
                            <el-table-column prop="name" label="标签" min-width="20%" sortable>
                                <template slot-scope="scope">
                                   <el-select placeholder="head标签" filterable v-model="scope.row.name">
                                       <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                   </el-select>
                                    <el-input class="selectInput" v-model="scope.row.name" :value="scope.row.name" placeholder="请输入内容"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column prop="value" label="内容" min-width="40%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="10%">
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
                        <div style="margin: 5px">
                            <el-row :span="24">
                                <el-col :span="4"><el-radio v-model="radio" label="form-data">表单(form-data)</el-radio></el-col>
                                <el-col :span="4"><el-radio v-model="radio" label="raw">源数据(raw)</el-radio></el-col>
                                <el-col :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterTyep">表单转源数据</el-checkbox></el-col>
                            </el-row>
                        </div>
                        <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
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
                            <el-table-column prop="description" label="参数说明" min-width="25%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.description" :value="scope.row.desc" placeholder="请输入参数说明"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="8%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px" @click="delParameter(scope.$index)"></i>
                                    <el-button type="primary" size="mini" style="margin-bottom: 5px" @click="handleParameterEdit(scope.$index, scope.row)">更多设置</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="5%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                     <template>
                         <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model="form.parameterRaw"></el-input>
                     </template>
                </el-collapse-item>
                    <el-dialog title="更多设置" v-model="addParameterFormVisible" :close-on-click-modal="false">
                        <el-form :model="editForm" label-width="60px" :rules="FormRules" ref="editForm" >
                            <el-form-item label="参数名" prop="name" label-width="83px">
                                <el-input v-model="editForm.name" auto-complete="off" placeholder="请输入参数名称"></el-input>
                            </el-form-item>
                            <el-form-item label="参数值" prop="name" label-width="83px">
                                <el-input v-model="editForm.value" auto-complete="off" placeholder="请输入参数值"></el-input>
                            </el-form-item>
                            <el-form-item label="必填?" label-width="83px" prop="required">
                                <el-select v-model="editForm.required" placeholder="必填？">
                                    <el-option v-for="(item,index) in required4" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="输入限制" prop='version' label-width="83px">
                                <el-input v-model="editForm.restrict" auto-complete="off" placeholder="请输入输入限制"></el-input>
                            </el-form-item>
                            <el-form-item label="描述" prop='description' label-width="83px">
                                <el-input type="textarea" :rows="7" v-model="editForm.description" placeholder="请输入描述"></el-input>
                            </el-form-item>
                        </el-form>
                        <div slot="footer" class="dialog-footer">
                            <el-button @click.native="addParameterFormVisible = false">取消</el-button>
                            <el-button type="primary" @click.native="editParameterSubmit">提交</el-button>
                        </div>
                    </el-dialog>
                <el-collapse-item title="返回参数" name="3">
                    <el-table :data="form.response" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'">
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
                        <el-table-column prop="description" label="参数说明" min-width="25%" sortable>
                            <template slot-scope="scope">
                               <el-input v-model="scope.row.description" :value="scope.row.desc" placeholder="请输入参数说明"></el-input>
                           </template>
                        </el-table-column>
                        <el-table-column label="操作" min-width="8%">
                            <template slot-scope="scope">
                                <i class="el-icon-delete" style="font-size:30px" @click="delResponse(scope.$index)"></i>
                                <el-button type="primary" size="mini" style="margin-bottom: 5px" @click="handleResponseEdit(scope.$index, scope.row)">更多设置</el-button>
                            </template>
                        </el-table-column>
                        <el-table-column label="" min-width="5%">
                            <template slot-scope="scope">
                                <el-button v-if="scope.$index===(form.response.length-1)" size="mini" class="el-icon-plus" @click="addResponse"></el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-collapse-item>
                    <el-dialog title="更多设置" v-model="addResponseFormVisible" :close-on-click-modal="false">
                        <el-form :model="editForm" label-width="60px" :rules="FormRules" ref="editForm" >
                            <el-form-item label="参数名" prop="name" label-width="83px">
                                <el-input v-model="editForm.name" auto-complete="off" placeholder="请输入参数名称"></el-input>
                            </el-form-item>
                            <el-form-item label="参数值" prop="name" label-width="83px">
                                <el-input v-model="editForm.value" auto-complete="off" placeholder="请输入参数值"></el-input>
                            </el-form-item>
                            <el-form-item label="必填?" label-width="83px" prop="required">
                                <el-select v-model="editForm.required" placeholder="必填？">
                                    <el-option v-for="(item,index) in required4" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="输入限制" prop='version' label-width="83px">
                                <el-input v-model="editForm.restrict" auto-complete="off" placeholder="请输入输入限制"></el-input>
                            </el-form-item>
                            <el-form-item label="描述" prop='description' label-width="83px">
                                <el-input type="textarea" :rows="7" v-model="editForm.description" placeholder="请输入描述"></el-input>
                            </el-form-item>
                        </el-form>
                        <div slot="footer" class="dialog-footer">
                            <el-button @click.native="addResponseFormVisible = false">取消</el-button>
                            <el-button type="primary" @click.native="editResponseSubmit">提交</el-button>
                        </div>
                    </el-dialog>
                <el-collapse-item title="普通mock" name="4">
                    <el-card class="box-card">
                      <div slot="header" class="clearfix">
                          <el-select v-model="form.mockCode" placeholder="HTTP状态">
                              <el-option v-for="(item,index) in httpCode" :key="index+''" :label="item.label" :value="item.value"></el-option>
                          </el-select>
                      </div >
                        <el-input v-model="form.mockData" type="textarea" :rows="8" placeholder="请输入mock内容"></el-input>
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
        Http: [{value: 'HTTP', label: 'HTTP'},][
                {value: 'HTTPS', label: 'HTTPS'}],
        checkHeadList: [],
        checkParameterList: [],
        ParameterTyep: true,
        group: [],
        radio: "form-data",
        secondGroup: [],
        status: [{value: 'True', label: '启用'},
                    {value: 'False', label: '禁用'}],
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
        addParameterFormVisible: false,
        addResponseFormVisible: false,
        required4:[{value: '1', label: '是'},
            {value: '0', label: '否'}],
        httpCode:[{value: '200', label: '200'},
            {value: '404', label: '404'},
            {value: '400', label: '400'},
            {value: '500', label: '500'},
            {value: '502', label: '502'},
            {value: '302', label: '302'}],
        radioType: "",
        result: true,
        activeNames: ['1', '2', '3', '4'],
        id: "",
        form: {
            firstGroup: '',
            secondGroup: '',
            name: '',
            status: 'True',
            request4: 'GET',
            Http4: 'HTTP',
            addr: '',
            head: [{name: "", value: ""},
            {name: "", value: ""}],
            parameterRaw: "",
            parameter: [{name: "", value: "", required:"1", restrict: "", description: ""},
            {name: "", value: "", required:"1", restrict: "", description: ""}],
            parameterType: "",
            response: [{name: "", value: "", required:"1", restrict: "", description: ""},
            {name: "", value: "", required:"1", restrict: "", description: ""}],
            mockCode: '',
            mockData: '',
        },
        FormRules: {
            name : [{ required: true, message: '请输入名称', trigger: 'blur' }],
            addr : [{ required: true, message: '请输入地址', trigger: 'blur' }],
            required : [{ required: true, message: '请输入地址', trigger: 'blur' }],
            firstGroup : [{ type: 'number', required: true, message: '请选择父分组', trigger: 'blur'}],
            secondGroup : [{ type: 'number', required: true, message: '请选择子分组', trigger: 'blur'}]
        },
        editForm: {
            name: "",
            value: "",
            required: "",
            restrict: "",
            description: "",
        },
        // editLoading: false
      }
    },
    methods: {
        addApi: function () {
            this.$refs.form.validate((valid) => {
                if (valid) {
                    let self = this;
                    this.$confirm('确认提交吗？', '提示', {}).then(() => {
                        self.form.parameterType = self.radio;
                        let _type = self.form.parameterType;
                        let _parameter;
                        if ( _type === 'form-data') {
                            if ( self.radioType === true) {
                                _type = 'raw'
                            }
                             _parameter = JSON.stringify(self.form.parameter);
                        } else {
                             _parameter = JSON.stringify(self.form.parameterRaw)
                        }
                        $.ajax({
                            type: "post",
                            url: test+"/api/api/add_api",
                            async: true,
                            data: { project_id: self.$route.params.project_id,
                            first_group_id: self.form.firstGroup,
                            second_group_id: self.form.secondGroup,
                            name: self.form.name,
                            httpType: self.form.Http4,
                            requestType: self.form.request4,
                            address: self.form.addr,
                            status: self.form.status,
                            headDict: JSON.stringify(self.form.head),
                            requestParameterType: _type,
                            requestList: _parameter,
                            responseList: JSON.stringify(self.form.response),
                            mockStatus: self.form.mockCode,
                            code: self.form.mockData},
                            headers: {
                                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                            },
                            timeout: 5000,
                            success: function(data) {
                                if (data.code === '999999') {
                                    self.$router.push({ name: "接口列表"});
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
        editParameterSubmit: function () {
			this.$refs.editForm.validate((valid) => {
				if (valid) {
                    this.form.parameter[this.id] = this.editForm;
                    this.addParameterFormVisible = false
                }
            })
        },
        handleParameterEdit: function (index, row) {
			this.addParameterFormVisible = true;
			this.id = index;
			this.editForm = Object.assign({}, row);
		},
        editResponseSubmit: function () {
			this.$refs.editForm.validate((valid) => {
				if (valid) {
                    this.form.response[this.id] = this.editForm;
                    this.addResponseFormVisible = false
                }
            })
        },
        handleResponseEdit: function (index, row) {
			this.addResponseFormVisible = true;
			this.id = index;
			this.editForm = Object.assign({}, row);
		},
        back(){
            this.$router.go(-1); // 返回上一层

        },
        // 获取api分组
        getApiGroup() {
            let self = this;
            $.ajax({
                type: "get",
                url: test+"/api/api/group",
                async: true,
                data: { project_id: this.$route.params.project_id},
                headers: {
                    Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                },
                timeout: 5000,
                success: function(data) {
                    if (data.code === '999999') {
                        self.group = data.data;
                        self.form.firstGroup = self.group[0].id
                    }
                    else {
                        self.$message.error({
                            message: data.msg,
                            center: true,
                        })
                    }
                },
            })
        },
        addHead() {
            let headers = {name: "", value: ""};
            this.form.head.push(headers)
        },
        delHead(index) {
            if (this.form.head.length !== 1) {
                this.form.head.splice(index, 1)
            }
        },
        addParameter() {
            let headers = {name: "", value: "", required:"True", restrict: "", description: ""};
            this.form.parameter.push(headers)
        },
        delParameter(index) {
            if (this.form.parameter.length !== 1) {
                this.form.parameter.splice(index, 1)
            }
        },
        addResponse() {
            let headers = {name: "", value: "", required:"True", restrict: "", description: ""};
            this.form.response.push(headers)
        },
        delResponse(index) {
            if (this.form.response.length !== 1) {
                this.form.response.splice(index, 1)
            }
        },
        changeSecondGroup(val) {
            this.secondGroup = [];
            this.form.secondGroup = "";
            for (let i=0; i<this.group.length; i++) {
                let id = this.group[i]['id'];
                if ( val === id) {
                    this.secondGroup = this.group[i].secondGroup
                }
            }
        },
        changeParameterType() {
            if (this.radio === 'form-data') {
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
      },
      fastAdd() {
        let form = this.$route.params.formData;
        let _type = this.$route.params._type;
        let _typeData = this.$route.params._typeData;
        if (form) {
            this.form.request4 = form.request4;
            this.form.Http4 = form.Http4;
            this.form.addr = form.addr;
            this.form.head = form.head;
            this.form.parameterRaw = form.parameterRaw;
            this.form.parameter = form.parameter;
            this.form.mockCode = form.statusCode;
            this.form.mockData = JSON.stringify(form.resultData)
        }
        if (_type) {
            this.radio = _type
        }
        if (_typeData) {
            this.radioType = _typeData
        }
      }
    },
    watch: {
        radio() {
            this.changeParameterType()
        }
    },
    mounted() {
        this.getApiGroup();
        this.fastAdd();
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
        margin-left: 7px;
        padding-left: 10px;
        width: 51%;
        height: 25px;
        left: 1px;
        top: 1px;
        border-bottom: 0px;
        border-right: 0px;
        border-left: 0px;
        border-top: 0px;
    }
</style>
