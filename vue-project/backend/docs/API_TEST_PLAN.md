# API测试计划 - 供应信息发布功能

## 🎯 测试目标
验证供应信息发布功能的完整性、正确性和安全性

## 📝 测试环境
- **后端服务**: http://localhost:5000
- **测试工具**: ApiFox / Postman
- **测试数据**: 使用init_db.py生成的测试数据

## 🧪 测试用例

### 1. 身份认证模块
| 用例ID | 测试场景 | 请求方法 | 端点 | 预期结果 |
|--------|----------|----------|------|----------|
| AUTH_001 | 正常登录 | POST | /api/auth/login | 200, 返回token |
| AUTH_002 | 错误密码 | POST | /api/auth/login | 401, 登录失败 |
| AUTH_003 | 获取用户信息 | GET | /api/auth/me | 200, 返回用户详情 |
| AUTH_004 | 无效token | GET | /api/auth/me | 401, token无效 |

### 2. 供应信息发布模块
| 用例ID | 测试场景 | 请求方法 | 端点 | 预期结果 |
|--------|----------|----------|------|----------|
| SUPPLY_001 | 发布供应信息 | POST | /api/supply/info | 201, 创建成功 |
| SUPPLY_002 | 获取供应列表 | GET | /api/supply/info | 200, 返回列表 |
| SUPPLY_003 | 获取供应详情 | GET | /api/supply/info/{id} | 200, 返回详情 |
| SUPPLY_004 | 更新供应信息 | PUT | /api/supply/info/{id} | 200, 更新成功 |
| SUPPLY_005 | 删除供应信息 | DELETE | /api/supply/info/{id} | 200, 删除成功 |
| SUPPLY_006 | 分页查询 | GET | /api/supply/info?page=1 | 200, 分页数据 |
| SUPPLY_007 | 条件筛选 | GET | /api/supply/info?status=ACTIVE | 200, 筛选结果 |

### 3. 药品数据模块
| 用例ID | 测试场景 | 请求方法 | 端点 | 预期结果 |
|--------|----------|----------|------|----------|
| DRUG_001 | 获取药品列表 | GET | /api/supply/drugs | 200, 药品列表 |
| DRUG_002 | 搜索药品 | GET | /api/supply/drugs?search=阿莫西林 | 200, 搜索结果 |

### 4. 权限控制测试
| 用例ID | 测试场景 | 请求方法 | 端点 | 预期结果 |
|--------|----------|----------|------|----------|
| PERM_001 | 未登录访问 | GET | /api/supply/info | 401, 需要认证 |
| PERM_002 | 非供应商发布 | POST | /api/supply/info | 403, 权限不足 |
| PERM_003 | 跨租户访问 | GET | /api/supply/info/{other_id} | 403, 数据隔离 |

### 5. 数据验证测试
| 用例ID | 测试场景 | 请求数据 | 预期结果 |
|--------|----------|----------|----------|
| VALID_001 | 缺少必填字段 | 不含drug_id | 422, 验证失败 |
| VALID_002 | 数据类型错误 | unit_price="abc" | 422, 类型错误 |
| VALID_003 | 数值范围验证 | available_quantity=-1 | 422, 数值无效 |
| VALID_004 | 日期格式验证 | valid_until="invalid" | 422, 日期格式错误 |

## 🔄 测试执行步骤

### Step 1: 准备测试环境
```bash
cd vue-project/backend
python init_db.py  # 初始化测试数据
python run.py      # 启动后端服务
```

### Step 2: 导入测试集合
1. ApiFox → 导入 → Postman Collection
2. 选择: Supply-Publish-API.postman_collection.json
3. 导入环境: dev-environment.postman_environment.json

### Step 3: 执行基础流程测试
```
1. 用户登录 → 获取token
2. 发布供应信息 → 记录supply_id
3. 获取供应列表 → 验证数据存在
4. 获取供应详情 → 验证完整信息
5. 更新供应信息 → 验证修改成功
6. 删除供应信息 → 验证删除成功
```

### Step 4: 执行边界测试
```
1. 权限验证 → 无token访问
2. 数据验证 → 无效参数
3. 业务逻辑 → 边界条件
4. 性能测试 → 响应时间
```

## 📊 测试数据

### 登录账号
```json
{
  "supplier1": {
    "username": "supplier1",
    "password": "password123",
    "role": "supplier",
    "tenant": "上海医药集团股份有限公司"
  },
  "pharmacy1": {
    "username": "pharmacy1", 
    "password": "password123",
    "role": "pharmacy",
    "tenant": "华润堂药房"
  }
}
```

### 测试药品
```json
{
  "drug_id": 1,
  "name": "阿莫西林胶囊",
  "specification": "0.25g*24粒/盒",
  "manufacturer": "石药集团"
}
```

## ✅ 验证检查点

### 功能验证
- [ ] 所有API接口响应正常
- [ ] 数据CRUD操作完整
- [ ] 分页和筛选功能正常
- [ ] 关联数据正确返回

### 安全验证  
- [ ] JWT token验证有效
- [ ] 角色权限控制正确
- [ ] 数据隔离机制有效
- [ ] 输入参数验证严格

### 性能验证
- [ ] 接口响应时间 < 2秒
- [ ] 数据库查询优化
- [ ] 大数据量处理正常

## 🐛 常见问题排查

### 422 错误
```
原因: 数据验证失败
解决: 检查请求参数格式和必填字段
```

### 401 错误  
```
原因: JWT token无效或过期
解决: 重新登录获取新token
```

### 403 错误
```
原因: 权限不足或跨租户访问
解决: 确认用户角色和数据权限
```

### 500 错误
```
原因: 服务器内部错误
解决: 查看后端日志，检查数据库连接
```
