<template>
  <div class="enterprise-auth">
    <div class="container">
      <div class="left-col">
        <div class="card roles">
          <h4>选择认证角色</h4>
          <div class="role-list">
            <div v-for="r in roles" :key="r.key" class="role" :class="{ active: selectedRole===r.key }" @click="selectedRole = r.key">
              <div class="icon">{{ r.icon }}</div>
              <div class="meta">
                <div class="title">{{ r.title }}</div>
                <div class="desc">{{ r.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card status">
          <h4>认证状态</h4>
          <div class="status-box">
            <div class="progress">
              <div class="bar" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="info">当前状态：<strong>{{ statusText }}</strong></div>
            <ul class="steps">
              <li>已完成1/3步</li>
              <li>资料提交：2025年10月28日 13:24</li>
              <li>资料审核：2025年10月29日 09:15</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="right-col">
        <div class="card auth-form">
          <h3>供应商资质认证</h3>
          <div class="form-grid">
            <div class="form-row">
              <label>企业名称</label>
              <input v-model="form.company" placeholder="填写企业名称" />
            </div>
            <div class="form-row">
              <label>统一社会信用代码</label>
              <input v-model="form.usci" placeholder="填入统一社会信用代码" />
            </div>
            <div class="form-row">
              <label>法定代表人</label>
              <input v-model="form.legal" placeholder="法人姓名" />
            </div>
            <div class="form-row">
              <label>企业联系人</label>
              <input v-model="form.contact" placeholder="联系人/电话" />
            </div>

            <div class="form-row upload-full">
              <label>资质文件上传</label>
              <div class="uploader" @drop.prevent="onDrop" @dragover.prevent>
                <div class="upload-area">
                  <div class="hint">拖拽文件到此处，或点击上传（支持 JPG/PNG/PDF，单个文件不超过 10MB）</div>
                  <input type="file" multiple @change="onFileChange" />
                </div>
                <ul class="file-list">
                  <li v-for="(f, i) in files" :key="i">
                    <span class="fname">{{ f.name }}</span>
                    <span class="fsize">{{ (f.size/1024/1024).toFixed(2) }}MB</span>
                    <button class="remove" @click.prevent="removeFile(i)">删除</button>
                  </li>
                </ul>
              </div>
            </div>

            <div class="form-row">
              <label>主要产品类别</label>
              <input v-model="form.productCategory" placeholder="例如：医疗器械" />
            </div>

            <div class="form-row full">
              <label>产品或资质说明</label>
              <textarea v-model="form.description" placeholder="填写产品或资质说明（可多行）"></textarea>
            </div>

            <div class="form-actions">
              <button class="secondary-btn" @click="saveDraft">保存草稿</button>
              <button class="primary-btn" @click="submitAuth">提交认证</button>
            </div>
          </div>
        </div>

        <div class="card review">
          <h4>审核反馈</h4>
          <div class="review-box">
            <div class="tag">审核未通过</div>
            <div class="time">2025年10月28日 15:42</div>
            <div class="notes">
              <p>需要补充的材料：</p>
              <ul>
                <li>医疗器械生产许可或进口许可扫描件</li>
                <li>GMP证书有效期请确认证明</li>
                <li>产品检验报告需附 CMA 资质</li>
              </ul>
              <p class="advice">审核意见：贵公司的 GMP 证书有效期为 2022-2025，需提交更新的证书或说明材料以完成审核。</p>
            </div>
            <div class="review-actions"><button class="primary-btn">重新提交材料</button></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const roles = [
  { key: 'enterprise', title: '商家认证', desc: '营业执照、药品资质、生产厂家', icon: '🏢' },
  { key: 'supplier', title: '供应商认证', desc: 'GMP 证书、生产许可、质检文件', icon: '📦' },
  { key: 'logistics', title: '物流认证', desc: '运输资质、冷链认证、运单凭证', icon: '🚚' },
  { key: 'regulator', title: '监管机构', desc: '官方机构、监管资质、机构编码', icon: '🏛️' }
]

const selectedRole = ref('enterprise')
const progress = ref(33)
const status = ref('rejected')

const statusText = computed(() => {
  if (status.value === 'approved') return '已通过'
  if (status.value === 'pending') return '审核中'
  return '审核未通过'
})

const form = ref({ company: '', usci: '', legal: '', contact: '', productCategory: '', description: '' })
const files = ref([])

function onFileChange(e) {
  const list = Array.from(e.target.files || [])
  list.forEach(f => files.value.push(f))
}

function onDrop(e) {
  const list = Array.from(e.dataTransfer.files || [])
  list.forEach(f => files.value.push(f))
}

function removeFile(i) { files.value.splice(i,1) }

function saveDraft() {
  // 简单示例：本地 console log
  console.log('保存草稿', { form: form.value, files: files.value, role: selectedRole.value })
  alert('草稿已保存（示例）')
}

function submitAuth() {
  // 简单验证示例
  if (!form.value.company) { alert('请填写企业名称'); return }
  if (!form.value.usci) { alert('请填写统一社会信用代码'); return }
  if (files.value.length === 0) { alert('请上传至少一份资质文件'); return }
  console.log('提交认证', { form: form.value, files: files.value })
  alert('认证已提交（示例）')
  // 模拟置为审核中
  status.value = 'pending'
  progress.value = 66
}
</script>

<style scoped>
.enterprise-auth { padding:20px; font-family: 'Microsoft YaHei', Arial, sans-serif }
.container { display:flex; gap:24px; max-width:1100px; margin:0 auto }
.left-col { width:320px; display:flex; flex-direction:column; gap:16px }
.right-col { flex:1; display:flex; flex-direction:column; gap:16px }
.card { background:#fff; border:1px solid #eef2f7; border-radius:8px; padding:16px }
.card h4, .card h3 { margin:0 0 12px 0 }
.role-list { display:flex; flex-direction:column; gap:10px }
.role { display:flex; gap:12px; padding:10px; border:1px solid #f0f3f7; border-radius:6px; cursor:pointer }
.role.active { border-color:#1a73e8; background:#f5faff }
.role .icon { width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#f3f6fb; border-radius:6px; font-size:18px }
.role .title { font-weight:600 }
.status .progress { height:8px; background:#f1f5f9; border-radius:6px; overflow:hidden; margin-bottom:8px }
.status .bar { height:100%; background:linear-gradient(90deg,#1a73e8,#3aa0ff) }
.status .info { margin-bottom:8px }
.status .steps { color:#666; font-size:13px; list-style:none; padding-left:0 }
.auth-form .form-grid { display:flex; flex-direction:column; gap:12px }
.form-row { display:flex; flex-direction:column }
.form-row label { color:#333; font-size:13px; margin-bottom:6px }
.form-row input, .form-row textarea { height:36px; padding:6px 10px; border:1px solid #d9d9d9; border-radius:4px; outline:none }
.form-row textarea { min-height:100px; height:auto; resize:vertical }
.upload-full .uploader { border:1px dashed #e6eef8; padding:12px; border-radius:6px; background:#fbfcfe }
.upload-area { position:relative }
.upload-area input[type=file] { position:absolute; left:0; top:0; width:100%; height:100%; opacity:0; cursor:pointer }
.upload-area .hint { color:#666; padding:14px 6px }
.file-list { margin-top:8px; list-style:none; padding-left:0 }
.file-list li { display:flex; justify-content:space-between; gap:10px; padding:6px 8px; border:1px solid #f1f4f8; border-radius:4px; margin-bottom:6px }
.file-list .remove { background:transparent; border:none; color:#e53e3e; cursor:pointer }
.form-actions { display:flex; gap:12px; justify-content:flex-end; margin-top:6px }
.primary-btn { background:#1a73e8; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer }
.secondary-btn { background:#fff; color:#333; border:1px solid #d9d9d9; padding:8px 16px; border-radius:6px; cursor:pointer }
.review .review-box { background:#fffbea; border:1px solid #f3e9c6; padding:12px; border-radius:6px }
.review .tag { display:inline-block; background:#fff3cd; color:#b76c00; padding:6px 10px; border-radius:4px; font-weight:600 }
.review .time { color:#666; margin-top:8px }
.review .notes { margin-top:8px; color:#333 }
.review .advice { margin-top:8px; color:#7b4b00 }

@media (max-width: 992px) {
  .container { flex-direction:column }
  .left-col { width:100% }
}
</style>
