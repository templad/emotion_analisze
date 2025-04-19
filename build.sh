#!/bin/bash

# 创建必要的目录
mkdir -p templates comment

# 复制模板文件到templates目录
cp app.html templates/
cp index.html templates/

# 复制为静态文件，确保直接访问
cp app.html ./app.html
cp index.html ./index.html
touch ./home

# 创建必要的评论文件
touch comment/comments.txt
touch comment/positive.txt
touch comment/neutral.txt
touch comment/negative.txt

echo "构建完成！" 