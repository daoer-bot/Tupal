<template>
  <div class="content-collector">
    <div class="collector-header">
      <h2 class="section-title">图文采集器</h2>
      <p class="section-subtitle">从网络采集优质图文内容，快速构建素材库</p>
    </div>

    <div class="collector-card glass-card-premium">
      <div class="input-group">
        <label class="input-label">输入内容链接</label>
        <input
          v-model="contentUrl"
          type="text"
          class="url-input glass-input"
          placeholder="粘贴小红书、微博等平台的内容链接..."
          @keyup.enter="handleCollect"
        />
      </div>

      <button
        class="btn-3d primary-action"
        @click="handleCollect"
        :disabled="!contentUrl || isCollecting"
      >
        <span v-if="isCollecting" class="loading-spinner"></span>
        {{ isCollecting ? '采集中...' : '开始采集' }}
      </button>
    </div>

    <div v-if="collectedContent" class="collected-preview glass-card-premium">
      <div class="preview-header">
        <h3>采集预览</h3>
        <button
          class="btn-3d save-btn"
          @click="handleSave"
          :disabled="isSaving"
        >
          <span v-if="isSaving" class="loading-spinner"></span>
          {{ isSaving ? '保存中...' : '保存到素材库' }}
        </button>
      </div>

      <div class="preview-content">
        <div class="content-meta">
          <div class="meta-item">
            <span class="meta-label">作者</span>
            <span class="meta-value">{{ collectedContent.author }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">标题</span>
            <span class="meta-value">{{ collectedContent.title }}</span>
          </div>
        </div>

        <div v-if="collectedContent.desc" class="content-description">
          <span class="meta-label">描述</span>
          <p>{{ collectedContent.desc }}</p>
        </div>

        <div v-if="collectedContent.cover" class="content-cover">
          <span class="meta-label">封面</span>
          <img :src="collectedContent.cover" alt="封面" class="preview-image" />
        </div>

        <div v-if="collectedContent.imgurl && collectedContent.imgurl.length" class="content-images">
          <span class="meta-label">图片 ({{ collectedContent.imgurl.length }})</span>
          <div class="image-grid">
            <img v-for="(img, idx) in collectedContent.imgurl" :key="idx" :src="img" alt="图片" class="preview-image" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import materialApi from '../../services/materialApi'

const router = useRouter()
const contentUrl = ref('')
const isCollecting = ref(false)
const isSaving = ref(false)
const collectedContent = ref<any>(null)

const handleCollect = async () => {
  if (!contentUrl.value) return

  isCollecting.value = true
  try {
    const response = await fetch('http://localhost:5030/api/xiaohongshu/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: contentUrl.value })
    })

    const result = await response.json()

    if (result.success) {
      collectedContent.value = result.data
    } else {
      alert('解析失败: ' + (result.error || '未知错误'))
    }
  } catch (error) {
    alert('请求失败: ' + error)
  } finally {
    isCollecting.value = false
  }
}

const handleSave = async () => {
  if (!collectedContent.value) return

  isSaving.value = true
  try {
    const response = await materialApi.createMaterial({
      name: collectedContent.value.title || '未命名素材',
      type: 'reference',
      category: '小红书采集',
      content: {
        author: collectedContent.value.author,
        title: collectedContent.value.title,
        description: collectedContent.value.desc,
        cover: collectedContent.value.cover,
        images: collectedContent.value.imgurl || [],
        source_url: contentUrl.value,
        reference_type: 'xiaohongshu'
      },
      description: collectedContent.value.desc || '',
      tags: ['小红书', '采集']
    })

    if (response.success && response.material_id) {
      // 跳转到素材库并高亮显示新素材
      router.push(`/workspace/knowledge?type=reference&highlight=${response.material_id}`)
    } else {
      alert('保存失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    alert('保存失败: ' + error)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.content-collector {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.collector-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.section-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

.collector-card {
  padding: 2rem;
  margin-bottom: 2rem;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.url-input {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.primary-action {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.collected-preview {
  padding: 2rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-header h3 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.content-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.meta-item {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-value {
  display: block;
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 500;
}

.content-description,
.content-cover,
.content-images {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.content-description p {
  margin: 0.5rem 0 0;
  line-height: 1.6;
  color: var(--text-primary);
}

.preview-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.75rem;
}

.image-grid .preview-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

@media (max-width: 768px) {
  .preview-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .save-btn {
    width: 100%;
  }

  .content-meta {
    grid-template-columns: 1fr;
  }
}
</style>