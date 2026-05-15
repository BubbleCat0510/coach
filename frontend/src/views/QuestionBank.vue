<template>
  <div class="question-bank-page">
    <el-card class="question-bank-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>题库管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索题目"
              clearable
              style="width: 200px; margin-right: 10px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon class="el-input__icon"><Search /></el-icon>
              </template>
            </el-input>
            <el-select 
              v-model="typeFilter" 
              placeholder="题目类型" 
              clearable
              style="width: 120px; margin-right: 10px;"
              @change="handleSearch"
            >
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multiple" />
              <el-option label="判断题" value="judge" />
            </el-select>
            <el-select 
              v-model="categoryFilter" 
              placeholder="分类" 
              clearable
              style="width: 120px; margin-right: 10px;"
              @change="handleSearch"
            >
              <el-option label="通用" :value="0" />
              <el-option label="商铺开发" :value="1" />
              <el-option label="品牌开发" :value="2" />
              <el-option label="品牌选址" :value="3" />
              <el-option label="上门服务" :value="4" />
              <el-option label="商铺招商" :value="5" />
            </el-select>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加题目
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="questionList"
        :style="{ width: '100%', height: tableHeight + 'px' }"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" header-align="center"></el-table-column>
        <el-table-column prop="question" label="题目内容" min-width="300" align="center" header-align="center">
          <template #default="scope">
            <div class="question-text">
              {{ scope.row.question }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="题目类型" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag size="small">{{ getQuestionType(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100" align="center" header-align="center">
          <template #default="scope">
            <el-tag :type="getDifficultyType(scope.row.difficulty)" size="small">
              {{ getDifficultyText(scope.row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag size="small">{{ getCategoryText(scope.row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="选项" width="150" align="left" header-align="center">
          <template #default="scope">
            <div class="options-list">
              <div v-for="(option, index) in getOptionsArray(scope.row.options)" :key="index" class="option-item">
                {{ option }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="正确答案" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag type="success" size="small">{{ getAnswerText(scope.row.type, scope.row.answer) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploaderName" label="上传人" width="120" align="center" header-align="center"></el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" align="center" header-align="center"></el-table-column>
        <el-table-column label="操作" width="180" align="center" header-align="center" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              icon="Edit"
              @click="handleEdit(scope.row)"
              style="margin-right: 5px;"
            >
              编辑
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="题目内容" prop="question">
          <el-input
            style="margin-right: 40px;"
            v-model="formData.question"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
          />
        </el-form-item>
        <el-form-item label="题目类型" prop="type">
          <el-select style="margin-right: 40px;" v-model="formData.type" placeholder="请选择题目类型">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="判断题" value="judge" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-select style="margin-right: 40px;" v-model="formData.difficulty" placeholder="请选择难度">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select style="margin-right: 40px;" v-model="formData.category" placeholder="请选择分类">
            <el-option label="通用" :value="0" />
            <el-option label="商铺开发" :value="1" />
            <el-option label="品牌开发" :value="2" />
            <el-option label="品牌选址" :value="3" />
            <el-option label="上门服务" :value="4" />
            <el-option label="商铺招商" :value="5" />
          </el-select>
        </el-form-item>
        
        <!-- 选项输入（单选和多选显示，判断隐藏） -->
        <el-form-item label="选项" prop="optionsArray" v-if="showOptions">
          <div class="options-container">
            <div class="option-row" v-for="(option, index) in formData.optionsArray" :key="index">
              <span class="option-label">{{ ['A', 'B', 'C', 'D'][index] }}.</span>
              <el-input
                v-model="formData.optionsArray[index]"
                :placeholder="`请输入选项${['A', 'B', 'C', 'D'][index]}`"
              />
            </div>
          </div>
        </el-form-item>
        
        <!-- 正确答案 -->
        <el-form-item label="正确答案" prop="answer">
          <!-- 判断题 -->
          <el-radio-group v-if="formData.type === 'judge'" v-model="formData.answer">
            <el-radio label="正确" value="正确" />
            <el-radio label="错误" value="错误" />
          </el-radio-group>
          
          <!-- 单选题 -->
          <el-radio-group v-else-if="formData.type === 'single'" v-model="formData.answer">
            <el-radio label="A" value="A" />
            <el-radio label="B" value="B" />
            <el-radio label="C" value="C" />
            <el-radio label="D" value="D" /> 
          </el-radio-group>
          
          <!-- 多选题 -->
          <el-checkbox-group v-else-if="formData.type === 'multiple'" v-model="formData.answerArray">
            <el-checkbox label="A" value="A" />
            <el-checkbox label="B" value="B" />
            <el-checkbox label="C" value="C" />
            <el-checkbox label="D" value="D" />
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getQuestionList, addQuestion, updateQuestion, deleteQuestion } from '../api/question'

// 状态管理
const questionList = ref([])
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(0)
const searchQuery = ref('')
const typeFilter = ref('') // 题目类型筛选
const categoryFilter = ref(null) // 分类筛选
const dialogVisible = ref(false)
const dialogTitle = ref('添加题目')
const formRef = ref(null)
const tableHeight = ref(460) // 表格高度，默认值
const formData = ref({
  id: null,
  question: '',
  type: 'single',
  difficulty: 'medium',
  category: '',
  optionsArray: ['', '', '', ''],
  answer: '',
  answerArray: []
})

// 表单验证规则
const rules = {
  question: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择题目类型', trigger: 'change' }
  ],
  difficulty: [
    { required: true, message: '请选择难度', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  optionsArray: [
    {
      validator: (rule, value, callback) => {
        if (formData.value.type === 'single' || formData.value.type === 'multiple') {
          const emptyOptions = value.map((opt, index) => ({ opt, index })).filter(item => !item.opt.trim())
          if (emptyOptions.length > 0) {
            const emptyLabels = emptyOptions.map(item => ['A', 'B', 'C', 'D'][item.index]).join('、')
            callback(new Error(`请填写选项${emptyLabels}`))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change']
    }
  ],
  answer: [
    {
      validator: (rule, value, callback) => {
        if (formData.value.type === 'judge') {
          if (!value) {
            callback(new Error('请选择正确答案'))
          } else {
            callback()
          }
        } else if (formData.value.type === 'single') {
          if (!value) {
            callback(new Error('请选择正确答案'))
          } else {
            callback()
          }
        } else if (formData.value.type === 'multiple') {
          if (formData.value.answerArray.length === 0) {
            callback(new Error('请选择正确答案'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 计算属性：是否显示选项
const showOptions = computed(() => {
  return formData.value.type === 'single' || formData.value.type === 'multiple'
})

// 监听题目类型变化
watch(() => formData.value.type, (newType) => {
  if (newType === 'judge') {
    formData.value.answer = '正确'
    formData.value.answerArray = []
  } else if (newType === 'single') {
    formData.value.answer = ''
    formData.value.answerArray = []
  } else if (newType === 'multiple') {
    formData.value.answer = ''
    formData.value.answerArray = []
  }
})

// 方法
const getQuestions = () => {
  getQuestionList({
    page: currentPage.value,
    page_size: pageSize.value,
    search: searchQuery.value,
    type: typeFilter.value || undefined,
    category: categoryFilter.value
  }).then(response => {
    if (response.success) {
      questionList.value = response.questions
      total.value = response.total
    } else {
      console.error('获取题目列表失败:', response.message)
      ElMessage.error('获取题目列表失败')
    }
  }).catch(error => {
    console.error('获取题目列表错误:', error)
    ElMessage.error('获取题目列表失败')
  })
}

const handleSearch = () => {
  currentPage.value = 1
  getQuestions()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  getQuestions()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  getQuestions()
}

const handleAdd = () => {
  dialogTitle.value = '添加题目'
  formData.value = {
    id: null,
    question: '',
    type: 'single',
    difficulty: 'medium',
    category: '',
    optionsArray: ['', '', '', ''],
    answer: '',
    answerArray: []
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑题目'
  // 解析选项
  const options = row.options ? row.options.split(',') : ['', '', '', '']
  const optionsArray = ['', '', '', '']
  options.forEach((opt, index) => {
    if (index < 4) {
      optionsArray[index] = opt.replace(/^[A-D]\./, '').trim()
    }
  })
  
  formData.value = {
    id: row.id,
    question: row.question,
    type: row.type,
    difficulty: row.difficulty,
    category: row.category,
    optionsArray: optionsArray,
    answer: row.type === 'multiple' ? '' : row.answer,
    answerArray: row.type === 'multiple' ? (row.answer ? row.answer.split('') : []) : []
  }
  dialogVisible.value = true
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除该题目吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteQuestion(id).then(response => {
      if (response.success) {
        ElMessage.success('删除成功')
        getQuestions()
      } else {
        ElMessage.error(response.message)
      }
    }).catch(error => {
      console.error('删除题目错误:', error)
      ElMessage.error('删除题目失败')
    })
  }).catch(() => {
    // 取消删除
  })
}

const handleSubmit = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      let answer = ''
      if (formData.value.type === 'judge') {
        answer = formData.value.answer
      } else if (formData.value.type === 'single') {
        answer = formData.value.answer
      } else if (formData.value.type === 'multiple') {
        answer = formData.value.answerArray.join('')
      }
      
      // 构建选项字符串（始终包含4个选项）
      let options = ''
      if (showOptions.value) {
        options = formData.value.optionsArray.map((opt, index) => {
          return `${['A', 'B', 'C', 'D'][index]}.${opt || ''}`
        }).join(',')
      }
      
      const data = {
        question: formData.value.question,
        answer: answer,
        type: formData.value.type,
        category: formData.value.category,
        difficulty: formData.value.difficulty,
        options: options
      }
      
      if (formData.value.id) {
        // 编辑
        updateQuestion(formData.value.id, data).then(response => {
          if (response.success) {
            ElMessage.success('编辑成功')
            dialogVisible.value = false
            getQuestions()
          } else {
            ElMessage.error(response.message)
          }
        }).catch(error => {
          console.error('更新题目错误:', error)
          ElMessage.error('更新题目失败')
        })
      } else {
        // 添加
        addQuestion(data).then(response => {
          if (response.success) {
            ElMessage.success('添加成功')
            dialogVisible.value = false
            getQuestions()
          } else {
            ElMessage.error(response.message)
          }
        }).catch(error => {
          console.error('添加题目错误:', error)
          ElMessage.error('添加题目失败')
        })
      }
    }
  })
}

const getQuestionType = (type) => {
  const typeMap = {
    'single': '单选题',
    'multiple': '多选题',
    'judge': '判断题'
  }
  return typeMap[type] || '未知'
}

const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return difficultyMap[difficulty] || '未知'
}

const getDifficultyType = (difficulty) => {
  const typeMap = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return typeMap[difficulty] || ''
}

const getCategoryText = (category) => {
  const categoryMap = {
    0: '通用',
    1: '商铺开发',
    2: '品牌开发',
    3: '品牌选址',
    4: '上门服务',
    5: '商铺招商'
  }
  // 处理字符串类型的数字
  const categoryNum = typeof category === 'string' ? parseInt(category, 10) : category
  return categoryMap[categoryNum] || category
}

const getOptionsArray = (options) => {
  if (!options) return []
  return options.split(',').filter(opt => opt.trim())
}

const getAnswerText = (type, answer) => {
  if (type === 'judge') {
    return answer === '正确' ? '正确' : '错误'
  }
  return answer || '-'
}

// 计算表格高度
const calculateTableHeight = () => {
  // 获取页面可用高度
  const windowHeight = window.innerHeight
  // 减去固定高度：顶部栏约80px + 卡片header约60px + 分页约60px + 边距约60px + 额外余量60px
  const offsetHeight = 320
  tableHeight.value = Math.max(400, windowHeight - offsetHeight)
}

// 生命周期
onMounted(() => {
  getQuestions()
  calculateTableHeight()
  // 监听窗口大小变化
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  // 移除监听
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.question-bank-page {
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

.question-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.option-label {
  font-weight: bold;
  width: 20px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-item {
  font-size: 13px;
  color: #666;
}
</style>
