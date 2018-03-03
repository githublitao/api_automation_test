<template>
    <section style="margin-left:15px">
        <el-button class="fastAddapi">快速新建API</el-button>
            <el-form>
                <el-row :span="24">
                <el-col :span="2" style="margin-right:10px">
                    <el-form-item>
                        <el-select v-model="request4" placeholder="请求方式">
                        <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="2" style="margin-right:10px">
                    <el-form-item>
                        <el-select v-model="Http4" placeholder="HTTP协议">
                        <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span='16' style="margin-right:10px">
                <el-form-item>
                    <el-input v-model="addr" placeholder="地址" clearable></el-input>
                </el-form-item>
                </el-col>
                <el-col :span='3'>
                <el-form-item>
                    <el-button type="primary">发送</el-button>
                </el-form-item>
                </el-col>
                </el-row>
                <el-col :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <template>
                            <el-checkbox-group v-model="checkList">
                                <div class="head-class">
                                    <el-row :span="24">
                                        <el-col :span="2">
                                        <span>头部</span>
                                        </el-col>
                                        <el-col :span="6">
                                        <span>标签</span>
                                        </el-col>
                                        <el-col :span="13">
                                        <span>内容</span>
                                        </el-col>
                                        <el-col :span="3">
                                        </el-col>
                                    </el-row>
                                </div>
                                <el-row :span="24">
                                    <el-col :span="2" style="margin-top:6px">
                                    <el-checkbox></el-checkbox>
                                    </el-col>
                                    <el-col :span="6">
                                    <el-form-item>
                                        <el-select v-model="header4" placeholder="head标签" filterable>
                                        <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="13">
                                    <el-form-item>
                                        <el-input v-model="addr" placeholder="内容" clearable></el-input>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="3">
                                    <i class="el-icon-delete" style="font-size:30px"></i>
                                    </el-col>
                                </el-row>
                                <el-row :span="24">
                                    <el-col :span="2" style="margin-top:6px">
                                    <el-checkbox></el-checkbox>
                                    </el-col>
                                    <el-col :span="6">
                                    <el-form-item>
                                        <el-select v-model="header4" placeholder="head标签" filterable>
                                        <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="13">
                                    <el-form-item>
                                        <el-input v-model="addr" placeholder="内容" clearable></el-input>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="3">
                                    <i class="el-icon-delete" style="font-size:30px"></i>
                                    </el-col>
                                </el-row>
                            </el-checkbox-group>
                        </template>
                    </el-collapse-item>
                     <el-collapse-item title="请求参数" name="2">
                         <template style="margin-top:6px">
                            <el-radio v-model="radio" label="1">表单(form-data)</el-radio>
                            <el-radio v-model="radio" label="2">源数据(raw)</el-radio>
                            <el-radio v-model="radio" label="3">表单转源数据</el-radio>
                        </template>
                        <template>
                            <el-checkbox-group v-model="checkList">
                                <div class="head-class">
                                    <el-row :span="24">
                                        <el-col :span="2">
                                        <span>头部</span>
                                        </el-col>
                                        <el-col :span="6">
                                        <span>参数名</span>
                                        </el-col>
                                        <el-col :span="13">
                                        <span>参数值</span>
                                        </el-col>
                                        <el-col :span="3">
                                        </el-col>
                                    </el-row>
                                </div>
                                <el-row :span="24">
                                    <el-col :span="2" style="margin-top:6px">
                                    <el-checkbox></el-checkbox>
                                    </el-col>
                                    <el-col :span="6">
                                    <el-form-item>
                                        <el-select v-model="header4" placeholder="head标签" filterable>
                                        <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="13">
                                    <el-form-item>
                                        <el-input v-model="addr" placeholder="内容" clearable></el-input>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="3">
                                    <i class="el-icon-delete" style="font-size:30px"></i>
                                    </el-col>
                                </el-row>
                                <el-row :span="24">
                                    <el-col :span="2" style="margin-top:6px">
                                    <el-checkbox></el-checkbox>
                                    </el-col>
                                    <el-col :span="6">
                                    <el-form-item>
                                        <el-select v-model="header4" placeholder="head标签" filterable>
                                        <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="13">
                                    <el-form-item>
                                        <el-input v-model="addr" placeholder="内容" clearable></el-input>
                                    </el-form-item>
                                    </el-col>
                                    <el-col :span="3">
                                    <i class="el-icon-delete" style="font-size:30px"></i>
                                    </el-col>
                                </el-row>
                            </el-checkbox-group>
                        </template>
                    </el-collapse-item>
                    <el-collapse-item title="响应结果" name="3">
                    </el-collapse-item>
                </el-collapse>
                </el-col>
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
        request4: 'get',
        Http: [{value: 'http', label: 'HTTP'},
                {value: 'https', label: 'HTTPS'}],
        Http4: 'http',
        addr: '',
        activeNames: ['1', '2', '3'],
        checkList: [],
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
        }
    },
    methods: {
        handleChange(val) {
      },
      onSubmit() {
        console.log('submit!');
      }
    }
  }
</script>

<style lang="scss" scoped>
 .fastAddapi {
    margin-top: 0px;
    margin-bottom: 10px;
    border-radius: 25px;
 }
 .head-class {
     font-size: 17px
 }
</style>
