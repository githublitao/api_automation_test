#!/bin/bash
set -e
cat /etc/gitlab/ssl/gitlab.example.com.crt
## 不需要更改的变量
# 发布分支
publish_branch=''
# 发布环境
publish_env=''
# release正则
release_reg='^(release/.+)$'
# release、tag、master正则
release_tag_master_reg='^(master|release/.+|v.+)$'
# 需要触发发布流程的正则
publish_reg='^(master|dev|pub|release/.+|v.+)$'
# 项目名
project=$CI_PROJECT_NAME
# 用于同步git.int的仓库名
project_remote="${project}-remote"

# 是tag发布先取tag名字
if [ -n "$CI_COMMIT_TAG" ]
then
  publish_branch=$CI_COMMIT_TAG
else
  publish_branch=$CI_COMMIT_REF_NAME
fi

# 如果发布分支为release或者tag或者master 发布环境名字改为prod
if [[ $publish_branch =~ $release_tag_master_reg ]]
then
  publish_env='prod'
else
  publish_env=$publish_branch
fi

## 不同项目需要改变的变量
# dev下存储目录
dev_file="dev@172.20.5.54:/home/dev/test_platform/"
# 预发布下存储目录
pre_publish_file=""
# cdn目录
export CDN_BASE_PATH="//s2.jiediankeji.com/${CI_PROJECT_NAME}/${publish_env}/"

# git远端地址
git_origin='https://git.int.ankerjiedian.com/jiedian/ankerbox-h5.git'
# git带账号密码的地址
git_origin_secret="https://${REMOTE_USERNAME}:${REMOTE_PASSWORD}@git.int.ankerjiedian.com/jiedian/ankerbox-h5.git"

# 红色高亮输出
log() {
  echo -e "\033[31m [$(date '+%Y-%m-%d %H:%M:%S')] $1 \033[0m"
}

# 非发布分支直接退出
if [[ ! "$publish_branch" =~ $publish_reg ]]
then
  exit
fi

log "当前发布分支:${publish_branch}"
log "当前发布环境:${publish_env}"

log "项目打包"

CDN_BASE_PATH=$CDN_BASE_PATH MODE=$publish_env
cd frontend
npm run build

log "上传静态文件"
if hash jd-upload 2>/dev/null; then
  jd-upload --version
else
  yarn add global https://s2.jiediankeji.com/tools/jd-uploader-master.tar
fi
cd ..
jd-upload --base "${CI_PROJECT_NAME}/${publish_env}/static/" --id $COS_ID --key $COS_KEY static/static

log "拷贝html到dev"
scp ./templates/index.html $dev_file
