<template>
    <section>
        <router-link :to="{ name: '新增接口', params: {project_id: this.$route.params.project_id, formData: this.form, _type: this.radio, _typeData: this.radioType}}" style='text-decoration: none;color: aliceblue;'>
                <el-button class="return-list">快速新建API</el-button>
            </router-link>
        <!--<el-button class="return-list">快速新建API</el-button>-->
        <el-form :model="form" ref="form" :rules="formRules">
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px;padding-bottom: 0px">
            <el-row :gutter="10">
                <el-col :span="3">
                    <el-form-item>
                        <el-select v-model="form.request4"  placeholder="请求方式">
                            <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="3">
                    <el-form-item>
                        <el-select v-model="form.Http4" placeholder="HTTP协议">
                            <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span='16'>
                    <el-form-item prop="addr">
                        <el-input v-model="form.addr" placeholder="地址" auto-complete></el-input>
                    </el-form-item>
                </el-col>
                <el-col :span='2'>
                    <el-button type="primary" @click="fastTest" :loading="loadingSend">发送</el-button>
                </el-col>
            </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row @selection-change="selsChangeHead" ref="multipleHeadTable">
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
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
                        <el-table :data="form.parameter" highlight-current-row :class="ParameterTyep? 'parameter-a': 'parameter-b'" @selection-change="selsChangeParameter" ref="multipleParameterTable">
                            <el-table-column type="selection" min-width="5%" label="头部">
                            </el-table-column>
                            <el-table-column prop="name" label="参数名" min-width="20%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column prop="value" label="参数值" min-width="40%" sortable>
                                <template slot-scope="scope">
                                   <el-input v-model="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>
                               </template>
                            </el-table-column>
                            <el-table-column label="操作" min-width="10%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px" @click="delParameter(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="10%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                     <template>
                         <el-input :class="ParameterTyep? 'parameter-b': 'parameter-a'" type="textarea" :rows="5" placeholder="请输入内容" v-model="form.parameterRaw"></el-input>
                     </template>
                </el-collapse-item>
                <el-collapse-item title="响应结果" name="4">
                    <div style="margin-bottom: 10px">
                        <el-button @click="showBody">Body</el-button>
                        <el-button @click="showHeader">Head</el-button>
                        <el-button type="primary" @click="neatenFormat">格式转换</el-button>
                    </div>
                    <el-card class="box-card">
                      <div slot="header" class="clearfix">
                        <span v-model="form.statusCode" style="font-size: 25px">{{form.statusCode}}</span>
                      </div>
                        <div v-model="form.resultData" :class="resultShow? 'parameter-a': 'parameter-b'" v-show="!format">{{form.resultData}}</div>
                        <div v-model="form.resultHead" :class="resultShow? 'parameter-b': 'parameter-a'">{{form.resultHead}}</div>
                        <div :class="resultShow? 'parameter-a': 'parameter-b'" v-show="format"><pre>{{form.resultData}}</pre></div>
                    </el-card>
                </el-collapse-item>
            </el-collapse>
            </el-row>
        </el-form>
    </section>
</template>
<script>
// import { POST } from '../../../api/api'
// import { GET } from '../../../api/api'
import $ from 'jquery'
import VuePopper from "element-ui/src/utils/vue-popper";
  export default {
      components: {VuePopper},
      data() {
      return {
        request: [{value: 'get', label: 'GET'},
                    {value: 'post', label: 'POST'},
                    {value: 'put', label: 'PUT'},
                    {value: 'delete', label: 'DELETE'}],
        Http: [{value: 'http', label: 'HTTP'},
                {value: 'https', label: 'HTTPS'}],
        ParameterTyep: true,
        radio: "form-data",
        loadingSend: false,
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
        radioType: "",
        result: true,
        activeNames: ['1', '2', '3', '4'],
        id: "",
        form: {
            request4: 'POST',
            Http4: 'HTTP',
            addr: '',
            head: [{name: "", value: ""},
            {name: "", value: ""}],
            parameterRaw: "",
            parameter: [{name: "", value: "", required:"", restrict: "", description: ""},
            {name: "", value: "", required:"", restrict: "", description: ""}],
            parameterType: "",
            statusCode: "",
            resultData: "",
            resultHead: "",
        },
        formRules: {
            addr: [
            { required: true, message: '请输入地址', trigger: 'blur' },
            ]
        },
        headers: "",
        parameters: "",
        resultShow: true,
        format: false,
      }
    },
    methods: {
        toggleHeadSelection(rows) {
              rows.forEach(row => {
                this.$refs.multipleHeadTable.toggleRowSelection(row, true);
              });
          },
        toggleParameterSelection(rows) {
              rows.forEach(row => {
                this.$refs.multipleParameterTable.toggleRowSelection(row, true);
              });
          },
        selsChangeHead: function (sels) {
			this.headers = sels
		},
        selsChangeParameter: function (sels) {
			this.parameters = sels
		},
        fastTest: function() {
            this.$refs.form.validate((valid) => {
                if (valid) {
                    this.loadingSend = true;
                    let self = this;
                    let _parameter = new Object();
                    let headers = new Object();
                    self.form.statusCode = '';
                    self.form.resultData = '';
                    self.form.resultHead = '';
                    for (let i = 0; i < self.headers.length; i++) {
                        var a = self.headers[i]["name"];
                        if (a) {
                            headers[a] = self.headers[i]["value"]
                        }
                    }
                    let url = self.form.Http4 + "://" + self.form.addr;
                    let _type = self.radio;
                    if (_type === 'form-data') {
                        console.log(self.radioType)
                        if (self.radioType) {
                            for (let i = 0; i < self.parameters.length; i++) {
                                var a = self.parameters[i]["name"];
                                if (a) {
                                    _parameter[a] = self.parameters[i]["value"];
                                }
                            }
                            _parameter = JSON.stringify(_parameter)
                        } else {
                            _parameter = self.form.parameter
                        }
                    } else {
                        // POST(url, self.form.parameterRaw, headers)
                        _parameter = self.form.parameterRaw;
                    }
                    $.ajax({
                        type: self.form.request4,
                        url: url,
                        async: true,
                        data: _parameter,
                        headers: headers,
                        timeout: 5000,
                        success: function (data, status, jqXHR) {
                            self.loadingSend = false;
                            self.form.statusCode = jqXHR.status;
                            self.form.resultData = data;
                            self.form.resultHead = jqXHR.getAllResponseHeaders()
                        },
                        error: function (jqXHR, error, errorThrown) {
                            self.loadingSend = false;
                            self.form.statusCode = jqXHR.status;
                            self.form.resultData = jqXHR.responseJSON;
                            self.form.resultHead = jqXHR.getAllResponseHeaders()
                        }
                    })
                }
            })
        },
        neatenFormat() {
            this.format = !this.format
        },
        addHead() {
            let headers = {name: "", value: ""};
            this.form.head.push(headers);
            let rows = [this.form.head[this.form.head.length-1]];
            this.toggleHeadSelection(rows)
        },
        delHead(index) {
            if (this.form.head.length !== 1) {
                this.form.head.splice(index, 1)
            }
        },
        addParameter() {
            let headers = {name: "", value: "", required:"True", restrict: "", description: ""};
            this.form.parameter.push(headers);
            let rows = [this.form.parameter[this.form.parameter.length-1]];
            this.toggleParameterSelection(rows)
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
        changeParameterType() {
            if (this.radio === 'form-data') {
                this.ParameterTyep = !this.ParameterTyep
            } else {
                this.ParameterTyep = !this.ParameterTyep
            }
        },
        showBody() {
            this.resultShow = true
        },
        showHeader() {
            this.resultShow = false
        },
        handleChange(val) {
      },
      onSubmit() {
        console.log('submit!');
      },
    },
    watch: {
        radio() {
            this.changeParameterType()
        }
    },
    mounted() {
        this.toggleHeadSelection(this.form.head);
        this.toggleParameterSelection(this.form.parameter)
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
        width:52%;
        height:25px;
        left:1px;
        top:1px;
        border-bottom:0px;
        border-right:0px;
        border-left:0px;
        border-top:0px;
    }

</style>
