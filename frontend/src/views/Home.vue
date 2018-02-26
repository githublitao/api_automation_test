<template>
  <el-container>
    <el-header><el-row :gutter="24">
      <el-row :gutter="24">
        <el-col :span="20"><div class="grid-content bg-purple-light">自动化测试平台</div></el-col>
        <el-col :span="3"><div class="grid-content bg-purple" v-bind="username">{{username}}</div></el-col>
        <el-col :span="1"><div class="grid-content head-portrait">
          <img :src='portrait' alt="头像" />
        </div></el-col>
      </el-row>
    </el-row></el-header>
    <el-container>
      <el-aside width="200px">Aside</el-aside>
      <el-main>Main</el-main>
    </el-container>
  </el-container>
</template>

<script>
/* eslint-disable */
  export default {
    data() {
      return {
        username: '李某',
        portrait:
      }
    }
  }
</script>

<style>
  .el-header, .el-footer {
    background-color: #B3C0D1;
    color: #333;
    line-height: 60px;
  }
  .el-aside {
    background-color: #D3DCE6;
    color: #333;
    text-align: center;
    line-height: 200px;
  }
  .el-main {
    background-color: #E9EEF3;
    color: #333;
    text-align: center;
    line-height: 160px;
  }
  body > .el-container {
    margin-bottom: 40px;
  }
  .el-container:nth-child(5) .el-aside,
  .el-container:nth-child(6) .el-aside {
    line-height: 260px;
  }
  .el-container:nth-child(7) .el-aside {
    line-height: 320px;
  }
  .el-row {
    margin-bottom: 20px;
    &:last-child {
      margin-bottom: 0;
    }
  }
  .el-col {
    border-radius: 4px;
  }
  .bg-purple-dark {
    background: #B3C0D1;
  }
  .bg-purple {
    background: #B3C0D1;
    text-align: right;
  }
  .bg-purple-light {
    background: #B3C0D1;
    text-align: left;
    font-size: 25px;
    font-family: Microsoft YaHei;
  }
  .grid-content {
    border-radius: 4px;
    min-height: 36px;
  }
  .row-bg {
    padding: 10px 0;
    background-color: #f9fafc;
  }
  .head-portrait {
    height: 60px;
    border-radius: 100px;
    width: 60px
  }
</style>
