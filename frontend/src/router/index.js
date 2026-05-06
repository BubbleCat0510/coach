// 引入创建路由所需的方法
import { createRouter, createWebHistory } from 'vue-router'

// 引入登录页面组件
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Train from '../views/Train.vue'
import Exam from '../views/Exam.vue'
import TrainingContent from '../views/TrainingContent.vue'
import Admin from '../views/Admin.vue'
import UserManagement from '../views/UserManagement.vue'
import FileUpload from '../views/FileUpload.vue'
import LearningStatus from '../views/LearningStatus.vue'
import QuestionBank from '../views/QuestionBank.vue'
import Profile from '../views/Profile.vue'
import ExamCenter from '../views/ExamCenter.vue'
import ExamTest from '../views/ExamTest.vue'
import MockTest from '../views/MockTest.vue'

// 定义路由规则
const routes = [
  // 访问 / 时，自动跳转到 /login
  {
    path: '/',
    redirect: '/login'
  },
  // 登录页面
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  // 员工登录后的"工作首页 / 控制台 页面
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  // AI 教练训练页面
  {
    path: '/train',
    name: 'Train',
    component: Train
  },
  // AI 测试页面
  {
    path: '/ai-test',
    name: 'Exam',
    component: Exam
  },
  // 评估中心页面
  {
    path: '/exam-center',
    name: 'ExamCenter',
    component: ExamCenter
  },
  // 正式测试页面
  {
    path: '/exam-test',
    name: 'ExamTest',
    component: ExamTest
  },
  // 模拟测试页面
  {
    path: '/mock-test',
    name: 'MockTest',
    component: MockTest
  },
  // 培训内容页面
  {
    path: '/training',
    name: 'TrainingContent',
    component: TrainingContent
  },
  // 管理员页面
  {
    path: '/admin',
    component: Admin,
    children: [
      {
        path: 'user',
        name: 'UserManagement',
        component: UserManagement
      },
      {
        path: 'file',
        name: 'FileUpload',
        component: FileUpload
      },
      {
        path: 'learning',
        name: 'LearningStatus',
        component: LearningStatus
      },
      {
        path: 'question',
        name: 'QuestionBank',
        component: QuestionBank
      },
      {
        path: '',
        name: 'Admin',
        redirect: '/admin/user'
      }
    ]
  },
  // 个人中心页面
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 读取登录态
  const token = localStorage.getItem('token')

  // 如果访问的是登录页，直接放行
  if (to.path === '/login') {
    next()
    return
  }

  // 访问其他页面，但没有 token
  if (!token) {
    next('/login')
    return
  }

  // 有 token，正常放行
  next()
})

// 导出给 main.js 使用
export default router
