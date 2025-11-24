// ApiFox/Postman 测试脚本
// 在每个请求的 Tests 标签页中添加以下脚本

// ====== 调试脚本：了解响应结构 ======
console.log("🔍 响应状态码:", pm.response.code);
console.log("🔍 响应头:", pm.response.headers.toString());

try {
    const jsonData = pm.response.json();
    console.log("📦 响应数据结构:");
    console.log("   - 根级字段:", Object.keys(jsonData));
    console.log("📄 完整响应数据:", JSON.stringify(jsonData, null, 2));
    
    // 检查常见的响应包装格式
    if (jsonData.data) {
        console.log("🎁 检测到data包装，内部结构:", Object.keys(jsonData.data));
    }
    if (jsonData.supply_info) {
        console.log("🎁 检测到supply_info包装");
    }
    if (jsonData.error) {
        console.log("❌ 检测到错误:", jsonData.error);
    }
} catch (e) {
    console.log("⚠️ 响应不是JSON格式:", pm.response.text());
}

// ====== 原有测试脚本 ======

// 1. 登录接口测试脚本
pm.test("登录状态码为200", function () {
    pm.response.to.have.status(200);
});

pm.test("返回access_token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.access_token).to.exist;
    // 自动设置环境变量
    pm.environment.set("token", jsonData.access_token);
});

pm.test("返回用户信息", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.user).to.exist;
    pm.expect(jsonData.user.role).to.equal("supplier");
    pm.expect(jsonData.user.tenant_id).to.exist;
});

// 2. 发布供应信息 - 完整示例

// ====== 前置操作 (Pre-request Script) ======
// 用途：准备测试数据和环境，不是用来测试的
/*
console.log("🔧 前置操作：准备测试数据");

// 1. 动态生成测试数据
const testSupplyData = {
    drug_id: pm.environment.get("test_drug_id") || Math.floor(Math.random() * 5) + 1,
    available_quantity: Math.floor(Math.random() * 1000) + 100,
    unit_price: parseFloat((Math.random() * 50 + 10).toFixed(2)),
    min_order_quantity: Math.floor(Math.random() * 50) + 10,
    valid_until: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    description: `测试供应信息 - ${new Date().toISOString()}`
};

// 2. 更新请求体
pm.request.body.raw = JSON.stringify(testSupplyData);

// 3. 保存预期值用于后续验证
pm.environment.set("expected_drug_id", testSupplyData.drug_id);
pm.environment.set("expected_quantity", testSupplyData.available_quantity);
pm.environment.set("expected_price", testSupplyData.unit_price);

// 4. 检查认证
const token = pm.environment.get("token");
if (!token) {
    console.warn("⚠️ 未找到token，请先执行登录");
}

console.log("📤 准备发送数据:", testSupplyData);
*/

// ====== 后置操作 (Tests) - 真正的测试部分 ======
// 根据实际API响应修正测试脚本
pm.test("发布供应信息成功", function () {
    pm.response.to.have.status(201);  
});

pm.test("返回供应信息ID", function () {
    var jsonData = pm.response.json();
    
    // 🔥 关键修正：实际响应有data包装层
    pm.expect(jsonData).to.have.property('data');
    pm.expect(jsonData.data).to.have.property('id');
    pm.expect(jsonData.data.id).to.be.a('number');
    
    // 设置供应信息ID用于后续测试
    pm.environment.set("supply_id", jsonData.data.id);
    
    console.log("✅ 供应信息创建成功，ID:", jsonData.data.id);
});

pm.test("供应信息数据完整", function () {
    var jsonData = pm.response.json();
    var supplyData = jsonData.data; // 获取data内的实际数据
    
    // 🔥 关键修正：访问data层内的字段
    pm.expect(supplyData).to.have.property('drug_id');
    pm.expect(supplyData).to.have.property('available_quantity');
    pm.expect(supplyData).to.have.property('unit_price');
    pm.expect(supplyData).to.have.property('status');
    
    // 验证关联对象存在
    pm.expect(supplyData).to.have.property('drug');
    pm.expect(supplyData).to.have.property('tenant');
    
    // 验证状态为激活
    pm.expect(supplyData.status).to.equal("ACTIVE");
    
    console.log("✅ 数据结构验证通过");
    console.log("📊 实际数据:", {
        id: supplyData.id,
        drug_id: supplyData.drug_id,
        quantity: supplyData.available_quantity,
        price: supplyData.unit_price,
        drug_name: supplyData.drug.brand_name
    });
});

// 3. 获取供应信息列表测试脚本
pm.test("获取列表状态码为200", function () {
    pm.response.to.have.status(200);
});

pm.test("返回分页数据", function () {
    var jsonData = pm.response.json();
    
    // 根据实际API响应结构调整
    // 如果是直接返回数组，使用items；如果有分页，使用pagination
    if (jsonData.items) {
        pm.expect(jsonData.items).to.be.an('array');
        pm.expect(jsonData).to.have.property('pagination');
        pm.expect(jsonData.pagination.total).to.be.at.least(0);
        pm.expect(jsonData.pagination.page).to.equal(1);
    } else if (Array.isArray(jsonData)) {
        // 如果直接返回数组
        pm.expect(jsonData).to.be.an('array');
        console.log("✅ 返回供应信息列表，共", jsonData.length, "条");
    }
});

// 4. 获取供应信息详情测试脚本
pm.test("获取详情状态码为200", function () {
    pm.response.to.have.status(200);
});

pm.test("返回详细信息", function () {
    var jsonData = pm.response.json();
    
    // 修正：直接验证根级字段
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('drug');
    pm.expect(jsonData).to.have.property('tenant');
    
    // 验证关联对象的基本结构
    pm.expect(jsonData.drug).to.have.property('generic_name');
    pm.expect(jsonData.tenant).to.have.property('name');
    
    console.log("✅ 供应信息详情:", {
        id: jsonData.id,
        drug: jsonData.drug.generic_name,
        tenant: jsonData.tenant.name
    });
});

// 5. 更新供应信息测试脚本
pm.test("更新供应信息成功", function () {
    pm.response.to.have.status(200);
});

pm.test("数据更新正确", function () {
    var jsonData = pm.response.json();
    
    // 修正：直接访问根级字段
    pm.expect(jsonData).to.have.property('available_quantity');
    pm.expect(jsonData).to.have.property('unit_price');
    
    // 如果有预期的更新值，从环境变量获取
    const expectedQuantity = pm.environment.get("updated_quantity");
    const expectedPrice = pm.environment.get("updated_price");
    
    if (expectedQuantity) {
        pm.expect(jsonData.available_quantity).to.equal(parseInt(expectedQuantity));
    }
    if (expectedPrice) {
        pm.expect(parseFloat(jsonData.unit_price)).to.equal(parseFloat(expectedPrice));
    }
    
    console.log("✅ 更新后数据:", {
        quantity: jsonData.available_quantity,
        price: jsonData.unit_price
    });
});

// 6. 错误处理测试
pm.test("权限验证", function () {
    // 当token无效时应返回401
    if (pm.response.code === 401) {
        pm.test("返回正确错误信息", function () {
            var jsonData = pm.response.json();
            pm.expect(jsonData.error).to.exist;
        });
    }
});

// 7. 通用响应时间测试
pm.test("响应时间小于2秒", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

// ========================================
// 前置操作 vs 后置操作 详细说明
// ========================================

/*
📋 前置操作 (Pre-request Script) - 执行请求之前
用途：准备工作，不是测试
┌─────────────────────────────────────────┐
│ 1. 数据准备    │ 生成动态测试数据         │
│ 2. 环境设置    │ 设置请求头、URL参数      │
│ 3. 认证检查    │ 验证token是否存在        │
│ 4. 请求修改    │ 动态修改请求内容         │
│ 5. 依赖检查    │ 确保前置条件满足         │
└─────────────────────────────────────────┘

示例前置脚本：
```javascript
// 数据准备
const dynamicData = {
    email: `test_${Date.now()}@example.com`,
    quantity: Math.floor(Math.random() * 100) + 1
};

// 更新请求
pm.request.body.raw = JSON.stringify(dynamicData);

// 认证设置
const token = pm.environment.get("token");
if (token) {
    pm.request.headers.upsert({
        key: 'Authorization',
        value: 'Bearer ' + token
    });
}

// 保存预期值
pm.environment.set("expected_email", dynamicData.email);

console.log("🔧 准备完成，即将发送请求");
```

✅ 后置操作 (Tests/Post-response Script) - 收到响应之后  
用途：验证和保存，这是真正的测试
┌─────────────────────────────────────────┐
│ 1. 响应验证    │ 状态码、数据结构验证     │
│ 2. 业务测试    │ 业务逻辑正确性测试       │
│ 3. 数据保存    │ 保存响应数据供后续使用   │
│ 4. 环境更新    │ 更新环境变量             │
│ 5. 条件判断    │ 根据响应设置后续行为     │
└─────────────────────────────────────────┘

示例后置脚本：
```javascript
// 1. 基础验证（测试）
pm.test("响应成功", function () {
    pm.response.to.have.status(200);
});

// 2. 数据验证（测试）
pm.test("数据格式正确", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData.email).to.equal(pm.environment.get("expected_email"));
});

// 3. 数据保存（非测试）
if (pm.response.code === 200) {
    const responseData = pm.response.json();
    pm.environment.set("user_id", responseData.id);
    pm.environment.set("user_email", responseData.email);
}

// 4. 条件判断（非测试）
const userRole = pm.response.json().role;
if (userRole === 'admin') {
    pm.environment.set("is_admin", "true");
}

console.log("✅ 验证完成，数据已保存");
```

🔄 执行流程：
前置操作 → 发送HTTP请求 → 后置操作

⚡ 关键区别：
┌──────────────┬──────────────┬──────────────┐
│   操作类型   │   执行时机   │   主要用途   │
├──────────────┼──────────────┼──────────────┤
│ 前置操作     │ 请求发送前   │ 数据准备     │
│ 后置操作     │ 收到响应后   │ 验证和保存   │
└──────────────┴──────────────┴──────────────┘

🎯 最佳实践：

1. 前置操作专注于：
   - 生成随机测试数据
   - 设置请求头和参数  
   - 检查依赖条件
   - 准备认证信息

2. 后置操作专注于：
   - pm.test() 测试断言
   - 保存响应数据
   - 更新环境变量
   - 记录测试结果

3. 数据流转：
   前置 → 保存预期值到环境变量
   后置 → 从环境变量获取预期值进行验证

这样分工明确，逻辑清晰！
*/
