<template>
  <div class="health-news-page">
    <div class="page-header">
      <div class="header-left">
        <h1>健康资讯中心</h1>
        <p class="subtitle">获取最新健康资讯与用药指南</p>
      </div>
      <el-button @click="goBack">返回首页</el-button>
    </div>

    <el-card shadow="never" class="news-container">
      <div v-loading="loading" class="news-list">
        <div v-if="newsList.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无健康资讯" />
        </div>
        
        <div v-for="news in newsList" :key="news.id" class="news-item" @click="showDetail(news)">
          <div class="news-content">
            <div class="news-title">{{ news.title }}</div>
            <div class="news-summary">{{ news.content }}</div>
            <div class="news-meta">
              <span class="news-source" v-if="news.source">{{ news.source }}</span>
              <span class="news-date">{{ news.publish_date }}</span>
              <el-tag v-if="news.level === 'important'" type="warning" size="small">重要</el-tag>
              <el-tag v-else-if="news.level === 'urgent'" type="danger" size="small">紧急</el-tag>
            </div>
          </div>
          <div class="news-arrow">›</div>
        </div>
      </div>

      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="currentNews?.title || '资讯详情'" width="600px">
      <div v-if="currentNews" class="news-detail">
        <div class="detail-meta">
          <span v-if="currentNews.source" class="source">来源：{{ currentNews.source }}</span>
          <span class="date">发布日期：{{ currentNews.publish_date }}</span>
        </div>
        <div class="detail-content">{{ currentNews.content }}</div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { homeApi } from '@/api/home'

const router = useRouter()

const loading = ref(false)
const newsList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const currentNews = ref(null)

const loadNews = async () => {
  loading.value = true
  try {
    const response = await homeApi.getHealthNews({
      page: currentPage.value,
      per_page: pageSize.value
    })
    if (response.data?.success !== false) {
      newsList.value = response.data?.data || response.data?.items || []
      total.value = response.data?.total || newsList.value.length
    }
  } catch (error) {
    console.error('加载健康资讯失败:', error)
    ElMessage.error('加载失败，请重试')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadNews()
}

const showDetail = (news) => {
  currentNews.value = news
  detailVisible.value = true
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  loadNews()
})
</script>

<style scoped>
.health-news-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-header .subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.news-container {
  border-radius: 8px;
}

.news-list {
  min-height: 300px;
}

.news-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.news-item:hover {
  background-color: #f5f7fa;
  margin: 0 -20px;
  padding: 16px 20px;
}

.news-item:last-child {
  border-bottom: none;
}

.news-content {
  flex: 1;
}

.news-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.news-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.news-source {
  color: #1a73e8;
}

.news-arrow {
  font-size: 24px;
  color: #c0c4cc;
  margin-left: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  margin-top: 10px;
}

.empty-state {
  padding: 40px 0;
}

.news-detail {
  padding: 10px 0;
}

.detail-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}
</style>
