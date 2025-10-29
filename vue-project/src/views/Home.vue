<template>
  <!-- 把你HTML中<body>里的所有页面内容放在这里 -->
  <div class="bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-md fixed w-full z-50">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center">
          <a href="#" class="flex items-center">
            <i class="fa fa-heartbeat text-primary text-2xl mr-2"></i>
            <span class="text-xl font-bold text-primary">上海药品监管平台</span>
          </a>
        </div>
        
        <!-- 桌面导航 -->
        <div class="hidden md:flex items-center space-x-8">
          <a href="#" class="nav-link text-gray-700 hover:text-primary">首页</a>
          <a href="#" class="nav-link text-gray-700 hover:text-primary">库存管理</a>
          <a href="#" class="nav-link text-gray-700 hover:text-primary">B2B供求平台</a>
          <a href="#" class="nav-link text-gray-700 hover:text-primary">流通监管</a>
          <a href="#" class="nav-link text-gray-700 hover:text-primary">智能调度</a>
        </div>
        
        <!-- 登录/注册按钮 -->
        <div class="hidden md:flex items-center space-x-4">
          <a href="#" class="px-4 py-2 text-primary hover:text-secondary transition-colors">登录</a>
          <a href="#" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-secondary transition-colors">注册</a>
          <a href="#" class="px-4 py-2 border border-primary text-primary rounded-md hover:bg-primary hover:text-white transition-colors">用户认证</a>
        </div>
        
        <!-- 移动端菜单按钮 -->
        <div class="md:hidden">
          <button @click="toggleMobileMenu" class="text-gray-700 focus:outline-none">
            <i class="fa fa-bars text-xl"></i>
          </button>
        </div>
      </div>
      
      <!-- 移动端导航菜单 -->
      <div v-show="mobileMenuOpen" class="md:hidden bg-white shadow-lg absolute w-full">
        <div class="container mx-auto px-4 py-3 flex flex-col space-y-4">
          <a href="#" class="text-gray-700 hover:text-primary py-2">首页</a>
          <a href="#" class="text-gray-700 hover:text-primary py-2">库存管理</a>
          <a href="#" class="text-gray-700 hover:text-primary py-2">B2B供求平台</a>
          <a href="#" class="text-gray-700 hover:text-primary py-2">流通监管</a>
          <a href="#" class="text-gray-700 hover:text-primary py-2">智能调度</a>
          <div class="flex flex-col space-y-2 pt-2 border-t border-gray-200">
            <a href="#" class="px-4 py-2 text-center text-primary hover:bg-gray-100 rounded-md transition-colors">登录</a>
            <a href="#" class="px-4 py-2 text-center bg-primary text-white rounded-md hover:bg-secondary transition-colors">注册</a>
          </div>
        </div>
      </div>
    </nav>

    <!-- 英雄区 -->
    <section class="hero-section relative h-96 overflow-hidden">
      <!-- 背景图片 -->
      <div class="absolute inset-0 z-0">
        <img src="https://p3-flow-imagex-sign.byteimg.com/tos-cn-i-a9rns2rl98/rc/pc/super_tool/bda2f5ac596a48c6bff2c70a855525df~tplv-a9rns2rl98-image.image?rcl=20251027141005D5ED568110FC180DE09C&amp;rk3s=8e244e95&amp;rrcfp=f06b921b&amp;x-expires=1764137420&amp;x-signature=TWKkOCOyIuBkjFkm8LMhj7QUg84%3D" alt="医疗健康" class="w-full h-full object-cover">
      </div>
      
      <!-- 3D球体画布 -->
      <div id="hero-canvas-container" class="absolute inset-0 z-10 opacity-70">
        <canvas ref="heroCanvas"></canvas>
      </div>
      
      <!-- 药丸装饰 -->
      <div class="pill pill-1"></div>
      <div class="pill pill-2"></div>
      <div class="pill pill-3"></div>
      <div class="pill pill-4"></div>
      <div class="pill pill-5"></div>
    </section>

    <!-- 核心功能服务 -->
    <section class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12 text-gray-800">核心功能服务</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 service-grid">
          <!-- 服务卡片1 - 药品库存管理 -->
          <div class="service-card bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <i class="fa fa-cubes service-icon text-green-600 text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-center mb-4 text-gray-800">药品库存管理</h3>
            <p class="text-gray-600 text-center mb-6">实时监控药品库存状况，自动提醒低库存药品，支持快速增补申请，确保药品供应充足。</p>
            <ul class="space-y-2 mb-6">
              <li class="flex items-center">
                <i class="fa fa-check text-green-500 mr-2"></i>
                <span class="text-gray-600">药品增补</span>
              </li>
              <li class="flex items-center">
                <i class="fa fa-check text-green-500 mr-2"></i>
                <span class="text-gray-600">低量警告提醒</span>
              </li>
            </ul>
            <div class="text-center">
              <a href="#" class="inline-block px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">开始管理</a>
            </div>
          </div>
          
          <!-- 服务卡片2 - 药品信息查询 -->
          <div class="service-card bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <i class="fa fa-user-md service-icon text-primary text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-center mb-4 text-gray-800">药品信息查询</h3>
            <p class="text-gray-600 text-center mb-6">快速查询超过10,00种药品信息，包含药品成分、使用说明及注意事项</p>
            <ul class="space-y-2 mb-6">
              <li class="flex items-center">
                <i class="fa fa-check text-green-500 mr-2"></i>
                <span class="text-gray-600">药品成分查询</span>
              </li>
              <li class="flex items-center">
                <i class="fa fa-check text-green-500 mr-2"></i>
                <span class="text-gray-600">用药指南</span>
              </li>
            </ul>
            <div class="text-center">
              <a href="#" class="inline-block px-6 py-2 bg-primary text-white rounded-md hover:bg-secondary transition-colors">立即查询</a>
            </div>
          </div>
          
          <!-- 服务卡片3 - 药品采购 -->
          <div class="service-card bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <i class="fa fa-medkit service-icon text-secondary text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-center mb-4 text-gray-800">药品采购</h3>
            <p class="text-gray-600 text-center mb-6">基于地理位置查找附近药房，实时获取营业时间与库存信息</p>
            <ul class="space-y-2 mb-6">
              <li class="flex items-center">
                <i class="fa fa-check text-green-500 mr-2"></i>
                <span class="text-gray-600">药品导航</span>
              </li>
              <li class="flex items-center">
                <i class="fa fa-check text-green-500 mr-2"></i>
                <span class="text-gray-600">供应商位置信息</span>
              </li>
            </ul>
            <div class="text-center">
              <a href="#" class="inline-block px-6 py-2 bg-secondary text-white rounded-md hover:bg-primary transition-colors">了解详情</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 红色通知栏 -->
    <section class="bg-red-600 text-white py-3">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa fa-bullhorn mr-2"></i>
            <span class="font-medium">重要通知：</span>
            <span>药品采购平台系统升级通知</span>
          </div>
          <div class="text-sm">2025-07-21</div>
        </div>
      </div>
    </section>
    
    <!-- 黄色公告区域 -->
    <section class="bg-yellow-100 border-l-4 border-yellow-500 py-4">
      <div class="container mx-auto px-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <i class="fa fa-info-circle text-yellow-500 text-xl"></i>
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700">
              <span class="font-medium">温馨提示：</span>
              为了保障您的用药安全，请在医生或药师指导下购买和使用药品。如有疑问，请咨询专业人士。
            </p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 特色服务 -->
    <section class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12 text-gray-800">特色服务</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- 服务卡片1 -->
          <div class="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 p-6">
            <div class="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <i class="fa fa-bell service-icon text-pink-500 text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-center mb-4 text-gray-800">个性化用药提醒</h3>
            <p class="text-gray-600 text-center mb-6">根据您的用药方案，提供个性化的用药提醒服务，帮助您按时按量服药，不错过任何一次用药。</p>
            <div class="text-center">
              <a href="#" class="inline-block px-6 py-2 bg-pink-500 text-white rounded-md hover:bg-pink-600 transition-colors">立即使用</a>
            </div>
          </div>
          
          <!-- 服务卡片2 -->
          <div class="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 p-6">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <i class="fa fa-money service-icon text-blue-500 text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-center mb-4 text-gray-800">药品价格对比</h3>
            <p class="text-gray-600 text-center mb-6">提供多家药房的药品价格对比服务，帮助您找到最实惠的药品购买渠道，节省用药成本。</p>
            <div class="text-center">
              <a href="#" class="inline-block px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors">立即查看</a>
            </div>
          </div>
          
          <!-- 服务卡片3 -->
          <div class="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 p-6">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <i class="fa fa-shield service-icon text-green-500 text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-center mb-4 text-gray-800">用药安全监测</h3>
            <p class="text-gray-600 text-center mb-6">实时监测您的用药情况，提供药物相互作用检查和不良反应预警，保障您的用药安全。</p>
            <div class="text-center">
              <a href="#" class="inline-block px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors">开始监测</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 全员拿U组 - 开发者介绍 -->
    <section class="py-20 bg-gradient-to-br from-blue-50 to-purple-50">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-800 mb-4">全员拿U组</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">我们是一支充满活力和创新精神的开发团队，专注于医疗健康领域的技术创新和服务优化。</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <!-- 团队图片 -->
          <div class="relative">
            <div class="absolute -inset-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg blur opacity-30"></div>
            <img src="https://p3-flow-imagex-sign.byteimg.com/tos-cn-i-a9rns2rl98/rc/pc/super_tool/b6b1b1a37119443c878d32be60643d68~tplv-a9rns2rl98-image.image?rcl=2025102715414263A001807D2D9C1D1387&amp;rk3s=8e244e95&amp;rrcfp=f06b921b&amp;x-expires=1764142985&amp;x-signature=nYjVcAWq1ZWCN9Ms%2Fmtq8NXDX0s%3D" alt="全员拿U组" class="relative rounded-lg shadow-xl w-full h-auto">
          </div>
          
          <!-- 团队介绍 -->
          <div>
            <h3 class="text-2xl font-bold text-gray-800 mb-6">关于我们</h3>
            <p class="text-gray-600 mb-8 text-lg">
              全员拿U组致力于通过技术创新提升医疗健康服务的效率和质量，为医疗机构和患者提供更好的数字化解决方案。
            </p>
            
            <!-- 核心成员 -->
            <h3 class="text-2xl font-bold text-gray-800 mb-6">核心成员</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">李可夫</h4>
                <p class="text-blue-600 mb-2">技术总监</p>
                <p class="text-gray-600">前BAT高级工程师，10年+全栈开发经验</p>
              </div>
              
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">吴彤</h4>
                <p class="text-purple-600 mb-2">产品经理</p>
                <p class="text-gray-600">医疗健康领域5年产品设计经验</p>
              </div>
              
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">李奕璇</h4>
                <p class="text-green-600 mb-2">医疗顾问</p>
                <p class="text-gray-600">资深医生，拥有丰富的临床经验</p>
              </div>
              
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">杜泉睿</h4>
                <p class="text-yellow-600 mb-2">UI/UX设计师</p>
                <p class="text-gray-600">专注于用户体验设计，追求极致的视觉效果</p>
              </div>
              
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">姜凯升</h4>
                <p class="text-red-600 mb-2">后端工程师</p>
                <p class="text-gray-600">专注于医疗数据处理和分析，AI算法专家</p>
              </div>
              
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">曾颢西</h4>
                <p class="text-indigo-600 mb-2">后端开发</p>
                <p class="text-gray-600">专注于高并发、高可用系统架构设计</p>
              </div>
              
              <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h4 class="font-semibold text-lg text-gray-800 mb-2">唐睿</h4>
                <p class="text-teal-600 mb-2">测试工程师</p>
                <p class="text-gray-600">确保产品质量和用户体验，医疗行业测试专家</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 团队优势 -->
        <div class="mt-20">
          <h3 class="text-2xl font-bold text-center mb-12 text-gray-800">我们的优势</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 mx-auto">
                <i class="fa fa-lightbulb-o text-blue-500 text-2xl"></i>
              </div>
              <h4 class="text-xl font-semibold text-center mb-4 text-gray-800">创新思维</h4>
              <p class="text-gray-600 text-center">我们不断探索医疗健康领域的创新点，将前沿技术与实际需求相结合，提供独特的解决方案。</p>
            </div>
            
            <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-6 mx-auto">
                <i class="fa fa-users text-purple-500 text-2xl"></i>
              </div>
              <h4 class="text-xl font-semibold text-center mb-4 text-gray-800">跨界团队</h4>
              <p class="text-gray-600 text-center">我们的团队由医疗专家和技术精英组成，能够从多个角度思考问题，提供全面的解决方案。</p>
            </div>
            
            <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6 mx-auto">
                <i class="fa fa-heartbeat text-green-500 text-2xl"></i>
              </div>
              <h4 class="text-xl font-semibold text-center mb-4 text-gray-800">用户至上</h4>
              <p class="text-gray-600 text-center">我们始终将用户需求放在首位，致力于提供安全、高效、便捷的医疗服务体验。</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="bg-gray-800 text-white py-12">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 class="text-xl font-semibold mb-4">医疗健康服务平台</h3>
            <p class="text-gray-400 mb-4">提供专业的医疗健康服务，守护您和家人的健康。</p>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fa fa-weixin text-xl"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fa fa-weibo text-xl"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fa fa-qq text-xl"></i>
              </a>
            </div>
          </div>
          
          <div>
            <h3 class="text-xl font-semibold mb-4">快速链接</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">首页</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">关于我们</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">服务项目</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">新闻资讯</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">联系我们</a></li>
            </ul>
          </div>
          
          <div>
            <h3 class="text-xl font-semibold mb-4">服务项目</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">在线医生咨询</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">药品配送服务</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">健康管理中心</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">体检预约</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">健康讲座</a></li>
            </ul>
          </div>
          
          <div>
            <h3 class="text-xl font-semibold mb-4">联系方式</h3>
            <ul class="space-y-2">
              <li class="flex items-center">
                <i class="fa fa-map-marker mr-2"></i>
                <span class="text-gray-400">北京市朝阳区健康路88号医疗大厦</span>
              </li>
              <li class="flex items-center">
                <i class="fa fa-phone mr-2"></i>
                <span class="text-gray-400">400-123-4567</span>
              </li>
              <li class="flex items-center">
                <i class="fa fa-envelope mr-2"></i>
                <span class="text-gray-400">contact@medicalhealth.com</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-700 mt-8 pt-8 text-center">
          <p class="text-gray-400">© 2025 医疗健康服务平台. 保留所有权利.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 移动端菜单状态
const mobileMenuOpen = ref(false)

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// Three.js相关
const heroCanvas = ref(null)
let scene, camera, renderer, sphere

// 初始化Three.js场景
const initThreeScene = () => {
  if (!heroCanvas.value) return

  // 创建场景
  scene = new THREE.Scene()
  
  // 创建相机
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = 5
  
  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas: heroCanvas.value,
    alpha: true,
    antialias: true
  })
  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(window.devicePixelRatio)
  
  // 创建球体几何体
  const geometry = new THREE.SphereGeometry(2, 64, 64)
  
  // 创建材质
  const material = new THREE.MeshPhongMaterial({
    color: 0x1e40af,
    transparent: true,
    opacity: 0.9,
    shininess: 100,
    specular: 0x333333
  })
  
  // 创建球体网格
  sphere = new THREE.Mesh(geometry, material)
  scene.add(sphere)
  
  // 添加光源
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
  directionalLight.position.set(5, 3, 5)
  scene.add(directionalLight)
  
  // 添加环境光
  const pointLight1 = new THREE.PointLight(0x3b82f6, 1)
  pointLight1.position.set(5, 5, 5)
  scene.add(pointLight1)
  
  const pointLight2 = new THREE.PointLight(0x8b5cf6, 1)
  pointLight2.position.set(-5, -5, 5)
  scene.add(pointLight2)
  
  // 开始动画
  animate()
}

// 动画函数
const animate = () => {
  requestAnimationFrame(animate)
  
  if (sphere) {
    // 旋转球体
    sphere.rotation.x += 0.002
    sphere.rotation.y += 0.005
    
    renderer.render(scene, camera)
  }
}

// 窗口大小变化处理
const handleResize = () => {
  if (camera && renderer) {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  }
}

// 页面滚动处理
const handleScroll = () => {
  const nav = document.querySelector('nav')
  if (window.scrollY > 50) {
    nav.classList.add('shadow-lg')
    nav.classList.remove('shadow-md')
  } else {
    nav.classList.remove('shadow-lg')
    nav.classList.add('shadow-md')
  }
}

// 组件挂载时执行
onMounted(() => {
  // 初始化Three.js场景
  initThreeScene()
  
  // 添加事件监听
  window.addEventListener('resize', handleResize)
  window.addEventListener('scroll', handleScroll)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 把你HTML中<style>里的所有CSS样式放在这里 */
.text-shadow {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.glass-effect {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.service-card {
  transition: all 0.3s ease;
}
.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

body {
  font-family: 'Inter', system-ui, sans-serif;
  overflow-x: hidden;
}

.hero-section {
  position: relative;
  height: 60vh;
  overflow: hidden;
  background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
}

#hero-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.nav-link {
  position: relative;
  transition: all 0.3s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.3);
}

.service-icon {
  transition: all 0.3s ease;
}

.service-card:hover .service-icon {
  transform: scale(1.1);
}

/* 药丸动画 */
@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.8;
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
    opacity: 1;
  }
  100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.8;
  }
}

.pill {
  position: absolute;
  border-radius: 50px;
  animation: float 6s infinite ease-in-out;
  z-index: 1;
}

.pill-1 {
  width: 40px;
  height: 16px;
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.pill-2 {
  width: 50px;
  height: 20px;
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
  top: 60%;
  left: 25%;
  animation-delay: 1s;
}

.pill-3 {
  width: 35px;
  height: 14px;
  background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
  top: 40%;
  left: 80%;
  animation-delay: 2s;
}

.pill-4 {
  width: 45px;
  height: 18px;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  top: 70%;
  left: 70%;
  animation-delay: 3s;
}

.pill-5 {
  width: 30px;
  height: 12px;
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
  top: 30%;
  left: 60%;
  animation-delay: 4s;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .hero-section {
    height: 80vh;
  }
  
  .service-grid {
    grid-template-columns: 1fr;
  }
}
</style>