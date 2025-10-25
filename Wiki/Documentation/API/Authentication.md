# 认证与用户管理 API

## 🔐 认证接口概览

认证模块提供用户注册、登录、令牌管理等基础认证功能，支持基于JWT的无状态认证机制。

### 接口列表
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/logout` - 用户登出
- `POST /auth/refresh` - 刷新访问令牌
- `POST /auth/forgot-password` - 忘记密码
- `POST /auth/reset-password` - 重置密码

---

## 📝 用户注册

### 接口地址
```
POST /api/v1/auth/register
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| username | string | 是 | 用户名，3-50字符，唯一 | `pharmacy001` |
| password | string | 是 | 密码，最少8位，包含字母和数字 | `Pass123456` |
| email | string | 条件必填 | 邮箱地址，唯一 | `user@example.com` |
| phone | string | 条件必填 | 手机号，唯一 | `13800138000` |
| real_name | string | 否 | 真实姓名 | `张三` |

> **注意：** email和phone至少填写一个

### 请求示例
```json
{
  "username": "pharmacy001",
  "password": "Pass123456",
  "email": "pharmacy@example.com",
  "phone": "13800138000",
  "real_name": "张三"
}
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "pharmacy001",
      "email": "pharmacy@example.com",
      "phone": "13800138000",
      "real_name": "张三",
      "role": "UNAUTHENTICATED",
      "tenant_id": null,
      "created_at": "2024-10-25T10:30:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400
  },
  "message": "注册成功"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "用户名已存在",
    "details": {
      "username": ["用户名已被使用"]
    }
  }
}
```

---

## 🔑 用户登录

### 接口地址
```
POST /api/v1/auth/login
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| username | string | 是 | 用户名或邮箱或手机号 | `pharmacy001` |
| password | string | 是 | 密码 | `Pass123456` |

### 请求示例
```json
{
  "username": "pharmacy001",
  "password": "Pass123456"
}
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "pharmacy001",
      "email": "pharmacy@example.com",
      "real_name": "张三",
      "role": "PHARMACY",
      "tenant": {
        "id": 1,
        "name": "上海某某药店",
        "address": "上海市浦东新区XX路123号"
      },
      "permissions": [
        "inventory:read",
        "inventory:create",
        "inventory:update",
        "orders:create",
        "orders:read",
        "supply_info:read"
      ],
      "last_login_at": "2024-10-25T10:30:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400
  },
  "message": "登录成功"
}
```

---

## 🚪 用户登出

### 接口地址
```
POST /api/v1/auth/logout
```

### 请求头
```
Authorization: Bearer <access_token>
```

### 响应示例
```json
{
  "success": true,
  "data": null,
  "message": "登出成功"
}
```

---

## 🔄 刷新访问令牌

### 接口地址
```
POST /api/v1/auth/refresh
```

### 请求参数
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400
  },
  "message": "令牌刷新成功"
}
```

---

## 📧 忘记密码

### 接口地址
```
POST /api/v1/auth/forgot-password
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| email | string | 条件必填 | 邮箱地址 | `user@example.com` |
| phone | string | 条件必填 | 手机号 | `13800138000` |

> **注意：** email和phone至少填写一个

### 请求示例
```json
{
  "email": "user@example.com"
}
```

### 响应示例
```json
{
  "success": true,
  "data": null,
  "message": "验证码已发送到您的邮箱"
}
```

---

## 🔧 重置密码

### 接口地址
```
POST /api/v1/auth/reset-password
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| token | string | 是 | 重置令牌 | `abc123def456` |
| verification_code | string | 是 | 验证码 | `123456` |
| new_password | string | 是 | 新密码 | `NewPass123` |

### 请求示例
```json
{
  "token": "abc123def456",
  "verification_code": "123456",
  "new_password": "NewPass123"
}
```

### 响应示例
```json
{
  "success": true,
  "data": null,
  "message": "密码重置成功"
}
```

---

## 👤 获取当前用户信息

### 接口地址
```
GET /api/v1/auth/me
```

### 请求头
```
Authorization: Bearer <access_token>
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "pharmacy001",
      "email": "pharmacy@example.com",
      "phone": "13800138000",
      "real_name": "张三",
      "role": "PHARMACY",
      "tenant": {
        "id": 1,
        "name": "上海某某药店",
        "address": "上海市浦东新区XX路123号",
        "contact_phone": "021-12345678"
      },
      "permissions": [
        "inventory:read",
        "inventory:create",
        "inventory:update",
        "orders:create",
        "orders:read",
        "supply_info:read"
      ],
      "last_login_at": "2024-10-25T10:30:00Z",
      "created_at": "2024-10-20T09:00:00Z"
    }
  }
}
```

---

## 🔐 修改密码

### 接口地址
```
PUT /api/v1/auth/change-password
```

### 请求头
```
Authorization: Bearer <access_token>
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| old_password | string | 是 | 原密码 | `OldPass123` |
| new_password | string | 是 | 新密码 | `NewPass123` |

### 请求示例
```json
{
  "old_password": "OldPass123",
  "new_password": "NewPass123"
}
```

### 响应示例
```json
{
  "success": true,
  "data": null,
  "message": "密码修改成功"
}
```

---

## 📝 更新用户信息

### 接口地址
```
PUT /api/v1/auth/profile
```

### 请求头
```
Authorization: Bearer <access_token>
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| real_name | string | 否 | 真实姓名 | `张三` |
| email | string | 否 | 邮箱地址 | `new@example.com` |
| phone | string | 否 | 手机号 | `13900139000` |

### 请求示例
```json
{
  "real_name": "张三",
  "email": "new@example.com",
  "phone": "13900139000"
}
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "pharmacy001",
      "email": "new@example.com",
      "phone": "13900139000",
      "real_name": "张三",
      "updated_at": "2024-10-25T11:00:00Z"
    }
  },
  "message": "用户信息更新成功"
}
```

---

## 🔒 验证令牌有效性

### 接口地址
```
POST /api/v1/auth/verify
```

### 请求参数
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user_id": 1,
    "expires_at": "2024-10-26T10:30:00Z"
  }
}
```

---

## ⚠️ 错误代码说明

| 错误代码 | HTTP状态码 | 说明 |
|----------|------------|------|
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `INVALID_CREDENTIALS` | 401 | 用户名或密码错误 |
| `USER_NOT_FOUND` | 404 | 用户不存在 |
| `USER_DISABLED` | 403 | 用户账户已被禁用 |
| `TOKEN_EXPIRED` | 401 | 访问令牌已过期 |
| `TOKEN_INVALID` | 401 | 访问令牌无效 |
| `EMAIL_ALREADY_EXISTS` | 409 | 邮箱已被使用 |
| `PHONE_ALREADY_EXISTS` | 409 | 手机号已被使用 |
| `USERNAME_ALREADY_EXISTS` | 409 | 用户名已被使用 |
| `VERIFICATION_CODE_INVALID` | 400 | 验证码错误或已过期 |
| `PASSWORD_TOO_WEAK` | 400 | 密码强度不够 |

---

## 🧪 测试用例

### Postman集合示例
```json
{
  "info": {
    "name": "SH-Drug-Mgmt Auth API",
    "description": "认证API测试集合"
  },
  "item": [
    {
      "name": "用户注册",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/auth/register",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"testuser\",\n  \"password\": \"TestPass123\",\n  \"email\": \"test@example.com\"\n}"
        }
      }
    },
    {
      "name": "用户登录",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/auth/login",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"testuser\",\n  \"password\": \"TestPass123\"\n}"
        }
      }
    }
  ]
}
```

---

## 📋 最佳实践

### 1. 密码安全
- 客户端在发送密码前应使用HTTPS加密
- 不要在客户端存储明文密码
- 定期提醒用户更换密码

### 2. 令牌管理
- 访问令牌有效期24小时
- 刷新令牌有效期7天
- 在令牌过期前主动刷新

### 3. 错误处理
- 统一处理认证错误
- 提供友好的错误提示
- 记录安全相关的异常

### 4. 性能优化
- 使用缓存减少数据库查询
- 实现令牌黑名单机制
- 控制API请求频率

---

**文档版本：** v1.0.0
**最后更新：** 2024-10-25
**维护团队：** 认证服务团队