# ApiFox本地环境测试快速指南

## 🚀 步骤总结

### 1. 确保本地服务器运行
```bash
# 在终端中确认Flask服务器正在运行
flask run
# 或
python run.py
```
**确认看到**: `Running on http://127.0.0.1:5000`

### 2. ApiFox环境配置
**创建环境**: `本地开发环境`
```
baseUrl: http://127.0.0.1:5000
token: (留空，登录后自动获取)
```

### 3. 测试脚本位置说明

#### 登录接口 (POST /api/auth/login)
- **前置脚本**: 留空或简单日志
- **后置操作 (Tests)**: 📋 **主要测试代码放这里**
```javascript
// 验证登录成功
pm.test("登录成功", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access_token');
    pm.expect(jsonData).to.have.property('user');
});

// 自动保存token
if (pm.response.code === 200) {
    const responseData = pm.response.json();
    pm.environment.set("token", responseData.access_token);
    pm.environment.set("user_id", responseData.user.id);
    pm.environment.set("user_role", responseData.user.role);
    
    console.log("✅ Token已保存:", responseData.access_token.substring(0, 20) + "...");
    console.log("✅ 用户信息:", responseData.user.username, responseData.user.role);
}
```

#### 获取用户信息 (GET /api/auth/me)
- **前置脚本**: Token检查和日志
- **后置操作 (Tests)**: 📋 **主要测试代码放这里**
```javascript
// 验证响应成功
pm.test("获取用户信息成功", function () {
    pm.response.to.have.status(200);
});

// 验证数据结构
pm.test("用户信息完整", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('username');
    pm.expect(jsonData).to.have.property('email');
    pm.expect(jsonData).to.have.property('role');
});

// 验证与登录信息一致
pm.test("用户信息一致", function () {
    const jsonData = pm.response.json();
    const expectedUserId = pm.environment.get("user_id");
    const expectedUserRole = pm.environment.get("user_role");
    
    if (expectedUserId) {
        pm.expect(jsonData.id.toString()).to.equal(expectedUserId.toString());
        console.log("✅ 用户ID匹配:", jsonData.id);
    }
    
    if (expectedUserRole) {
        pm.expect(jsonData.role).to.equal(expectedUserRole);
        console.log("✅ 用户角色匹配:", jsonData.role);
    }
});
```

## 📋 操作流程

### 步骤1: 测试登录
1. **选择接口**: `POST /api/auth/login`
2. **Body数据**:
```json
{
  "username": "supplier1",
  "password": "password123"
}
```
3. **添加后置脚本**: 复制上面的登录测试代码
4. **发送请求**: 应该返回200状态码和真实的token

### 步骤2: 测试获取用户信息
1. **选择接口**: `GET /api/auth/me`
2. **添加前置脚本**: Token检查代码
3. **添加后置脚本**: 用户信息验证代码
4. **发送请求**: 应该返回与登录用户一致的信息

### 步骤3: 测试业务接口
1. **选择接口**: 如 `POST /api/supply/info`
2. **确认token**: 自动从环境变量获取
3. **添加测试脚本**: 验证业务逻辑
4. **发送请求**: 测试CRUD操作

## ✅ 关键要点

1. **本地环境**: 使用 `http://127.0.0.1:5000` 获得真实业务逻辑
2. **测试位置**: 主要测试代码放在 **"后置操作 (Tests)"** 标签
3. **自动化**: 登录后token自动保存，后续接口自动使用
4. **数据一致性**: 发送什么数据，就返回对应的真实数据
5. **完整验证**: 可以测试完整的业务流程和数据验证

## 🎯 测试效果

使用本地环境，您会看到：
- ✅ 发送 `supplier1` → 返回 `supplier1` 的真实数据
- ✅ Token有效性验证
- ✅ 完整的业务逻辑测试
- ✅ 真实的错误处理

这样就可以进行完整、可靠的API测试了！
