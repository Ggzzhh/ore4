记录用文档
-------
### 创建空环境
```sybase
virtualenv --no-site-packages venv
```
### 登录次数限制
    一天内错误次数达到10次自动锁定账号
    提取数据库中该账号今天输入错误的次数以及时间
    天数不一样重置次数为0
    次数到达限制后锁定账户

### 返回可查看人员名单
    如果角色是管理员或者领导，则返回所有人资料
    如果角色是干部，则返回干部本科室的资料
    如果角色是员工，则返回员工自己的资料


### 关于导入时部门的问题
    导入前提示：如果没有预先把部门添加到设置中，导入时部门为空。
    例：张三是人事科的，但是部门分类中没有人事科，那么在导入张三的数据时他的部门会为空
    
### 关于flask-moment语言问题
    在include_moment()下面添加{{ moment.lang("zh-cn") }}
    
### jinja2中使用break以及continue
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')