<template>
  <div class="file-upload-page">
    <!-- 文件列表 -->
    <el-card class="file-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>文件列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索文件名称"
              clearable
              style="width: 300px; margin-right: 10px;"
              @keyup.enter="handleSearch"
              @input="handleSearch"
              @clear="handleSearch"
            >
              <template #prefix>
                <el-icon class="el-input__icon"><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openUploadDialog">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="fileListData"
        :style="{ width: '100%', height: tableHeight + 'px' }"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" header-align="center"></el-table-column>
        <el-table-column prop="name" label="文件名称" min-width="300" align="center" header-align="center">
          <template #default="scope">
            <div class="file-name">
              {{ scope.row.name }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="文件分类" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag size="small">{{ getCategoryText(scope.row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="所属岗位" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag size="small" :type="getRoleTagType(scope.row.role)">{{ getRoleText(scope.row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="文件类型" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag size="small">{{ getFileTypeText(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploadTime" label="上传时间" width="200" align="center" header-align="center">
          <template #default="scope">
            {{ scope.row.uploadTime }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" header-align="center">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              icon="Download" 
              @click="handleDownload(scope.row)"
              style="margin-right: 5px;"
            >
              下载
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              icon="Delete" 
              @click="handleDelete(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 上传文件弹窗 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文件"
      width="650px"
    >
      <el-form label-width="100px">
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            class="upload-drag-inner"
            drag
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            :before-upload="handleBeforeUpload"
            :file-list="fileList"
            :limit="1"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mov,.wmv,.flv,.mp3,.wav"
          >
            <el-icon class="el-icon--upload large-icon"><Upload /></el-icon>
            <div class="upload-text">拖拽文件到此处或 <em>点击上传</em></div>
            <div class="upload-hint">支持 PDF、Word、Excel、PowerPoint、图片、视频、音频等格式，最大500MB</div>
          </el-upload>
        </el-form-item>
        <el-form-item label="文件分类">
          <el-select
            v-model="fileCategory"
            placeholder="请选择文件分类"
            style="width: 100%;margin-right: 40px;"
          >
            <el-option label="技术文档" value="technical" />
            <el-option label="培训资料" value="training" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属岗位">
          <el-select
            v-model="fileRole"
            placeholder="请选择所属岗位"
            style="width: 100%;margin-right: 40px;"
          >
            <el-option label="商铺开发" :value="1" />
            <el-option label="上门服务" :value="2" />
            <el-option label="品牌开发" :value="3" />
            <el-option label="商铺招商" :value="4" />
            <el-option label="品牌选址" :value="5" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpload">上传</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Search, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadFile, getFileList, deleteFile as deleteFileApi } from '@/api/upload'

// 状态管理
const fileList = ref([])
const fileListData = ref([])
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(0)
const searchQuery = ref('')
const fileCategory = ref('technical')
const fileRole = ref(1) // 默认选择第一个岗位
const uploadDialogVisible = ref(false)
const uploadRef = ref(null)
const tableHeight = ref(460)

// 方法
const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB

const openUploadDialog = () => {
  fileList.value = []
  fileCategory.value = 'technical'
  fileRole.value = 1 // 重置为第一个岗位
  // 清空上传组件的内部状态
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  uploadDialogVisible.value = true
}

// 文件选择变化时触发
const handleFileChange = (file, uploadFileList) => {
  console.log('handleFileChange - file:', file)
  console.log('handleFileChange - uploadFileList:', uploadFileList)
  console.log('handleFileChange - 响应式 fileList.value:', fileList.value)
  
  // 检查文件大小
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.warning('文件大小不能超过500MB')
    // 清空上传组件的内部状态
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
    // 清空响应式变量
    fileList.value = []
    return
  }
  
  // 文件通过校验，更新响应式 fileList
  // Element Plus 的 on-change 会自动更新 file-list，但我们手动同步确保一致性
  console.log('文件校验通过，文件名:', file.name, '大小:', file.size)
  fileList.value = uploadFileList
}

// 使用 before-upload 钩子统一处理文件校验（上传前再次校验）
const handleBeforeUpload = (file) => {
  console.log('handleBeforeUpload - file:', file)
  
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.warning('文件大小不能超过500MB')
    // 清空上传组件的内部状态
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
    return false
  }
  
  console.log('before-upload 校验通过')
  // 返回 false 阻止自动上传（手动控制上传）
  return false
}

const handleUpload = () => {
  console.log('handleUpload - fileList.value:', fileList.value)
  console.log('handleUpload - fileList.value.length:', fileList.value.length)
  
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  // 检查文件对象结构
  const selectedFile = fileList.value[0]
  console.log('handleUpload - selectedFile:', selectedFile)
  console.log('handleUpload - selectedFile.raw:', selectedFile?.raw)
  
  if (!selectedFile?.raw) {
    ElMessage.warning('文件对象格式不正确')
    return
  }

  uploadFile(selectedFile.raw, fileCategory.value, fileRole.value).then(res => {
    ElMessage.success('上传成功')
    fileList.value = []
    fileCategory.value = 'technical'
    fileRole.value = 1
    uploadDialogVisible.value = false
    getFiles()
  }).catch(err => {
    console.error('上传文件错误:', err)
  })
}

// 防抖定时器
let searchTimer = null

const getFiles = () => {
  getFileList(currentPage.value, pageSize.value, searchQuery.value).then(res => {
    fileListData.value = res.files || []
    total.value = res.total || 0
  }).catch(err => {
    console.error('获取文件列表错误:', err)
  })
}

const handleSearch = () => {
  // 防抖处理：300ms内多次输入只执行最后一次
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    getFiles()
  }, 300)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  getFiles()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  getFiles()
}

const handleDownload = (row) => {
  // 创建隐藏的a标签来触发下载
  const downloadUrl = `/api/upload/download/${row.id}`
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = row.name || 'download'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除该文件吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteFileApi(id).then(res => {
      ElMessage.success('删除成功')
      getFiles()
    }).catch(err => {
      console.error('删除文件错误:', err)
    })
  }).catch(() => {
    // 取消删除
  })
}

const getCategoryText = (category) => {
  // 将分类值映射到通俗易懂的分类名称
  const categoryMap = {
    'technical': '技术文档',
    'training': '培训资料',
    'other': '其他'
  }
  return categoryMap[category] || '其他'
}

// 岗位映射
const roleMap = {
  1: '商铺开发',
  2: '上门服务',
  3: '品牌开发',
  4: '商铺招商',
  5: '品牌选址'
}

// 获取岗位文本
const getRoleText = (role) => {
  return roleMap[role] || '其他'
}

// 获取岗位标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    1: 'primary',    // 商铺开发 - 蓝色
    2: 'success',    // 上门服务 - 绿色
    3: 'warning',    // 品牌开发 - 橙色
    4: 'danger',     // 商铺招商 - 红色
    5: 'info'        // 品牌选址 - 灰色
  }
  return typeMap[role] || 'info'
}

const getFileTypeText = (fileType) => {
  // 将MIME类型映射到通俗易懂的文件类型
  const typeMap = {
    // 文档类型
    'application/pdf': 'PDF文档',
    'application/msword': 'Word文档',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word文档',
    'application/vnd.ms-excel': 'Excel表格',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel表格',
    'application/vnd.ms-powerpoint': 'PowerPoint演示',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint演示',
    'text/plain': '文本文件',
    'text/html': 'HTML文件',
    // 图片类型
    'image/jpeg': '图片',
    'image/png': '图片',
    'image/gif': '图片',
    'image/bmp': '图片',
    'image/webp': '图片',
    // 视频类型
    'video/mp4': '视频',
    'video/avi': '视频',
    'video/mpeg': '视频',
    'video/quicktime': '视频',
    'video/x-ms-wmv': '视频',
    'video/webm': '视频',
    'video/mpg': '视频',
    'video/mov': '视频',
    // 音频类型
    'audio/mpeg': '音频',
    'audio/wav': '音频',
    'audio/ogg': '音频',
    'audio/flac': '音频',
    'audio/mp3': '音频',
    'audio/x-wav': '音频',
    // 压缩文件
    'application/zip': '压缩文件',
    'application/rar': '压缩文件',
    'application/x-7z-compressed': '压缩文件'
  }
  return typeMap[fileType] || '其他文件'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 计算表格高度
const calculateTableHeight = () => {
  const windowHeight = window.innerHeight
  const offsetHeight = 320
  tableHeight.value = Math.max(400, windowHeight - offsetHeight)
}

// 生命周期
onMounted(() => {
  getFiles()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.file-upload-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.upload-drag-inner {
  margin-right: 40px;
  width: 100%;
}

.upload-drag-inner :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
  
  border-radius: 12px;
}

.upload-drag-inner :deep(.el-upload-dragger:hover) {
  border-color: #2e8b57;
  background-color: #f0fdf4;
}

.large-icon {
  font-size: 48px;
  color: #2e8b57;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 13px;
  color: #999;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>