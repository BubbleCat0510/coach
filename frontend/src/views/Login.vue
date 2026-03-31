<template>
  <!-- 整个页面的最外层容器，用来撑满屏幕 -->
  <div class="login-page">
    <!-- 登录卡片 -->
    <el-card class="login-card">
      <!-- 呱太logo -->
      <div class="frog-icon">
        <!-- 使用 :src 绑定导入的变量 -->
        <img :src="logo" alt="呱太小哥 Logo" />
      </div>

      <!-- 标题 -->
      <h2 class="title">AI 冠军教练</h2>

      <!-- 登录表单 -->
      <el-form :model="form" @submit.prevent="handleLogin">
        <!-- 账号输入框 -->
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="请输入账号"
            size="large"
          />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          />
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
            type="primary"
						native-type="submit"
            size="large"
            style="width: 100%;"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
// 引入 Vue 3 的响应式 API
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'
import { useRouter } from 'vue-router'
//  导入呱太在线直租的logo
import logo from '@/assets/guatai_transparent_logo.png'

// 路由实例
const router = useRouter()

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

// 点击登录
const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号或密码')
    return
  }

  try {
    const res = await login(form)

    console.log('请求参数：', form)
    console.log('登录账号：', form.username)
    console.log('登录密码：', form.password)
    console.log('登录返回：', res)

    if (res.success) {
      ElMessage.success('登录成功')

      // ✅ 保存登录态（token）
      localStorage.setItem('token', res.token)

      // 跳转到工作台
      router.push('/dashboard')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (err) {
    ElMessage.error('请求失败')
  }
}
</script>

<style scoped>
/* 页面最外层 */
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 使用推荐的清新自然风绿色 */
  background: linear-gradient(135deg, #90EE90, #98FB98);
}

/* 登录卡片 */
.login-card {
  width: 420px;
  padding: 30px;
  border-radius: 12px;
  background: white; /* 卡片保持白色，突出内容 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

/* 青蛙图标 */
.frog-icon {
  text-align: center;
  margin-bottom: 20px;
}

.frog-icon img {
  width: 190px;
  height: 150px;
  object-fit: contain; /* 保持图片比例 */
  /* 如果图片边缘有锯齿，可以尝试下面的属性 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}

/* 标题样式 - 使用楷体 */
.title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
  color: #2e8b57; /* 使用公司主色 */
  /* 使用楷体 */
  /* font-family: "KaiTi", "STKaiti", serif; */
}

/* 按钮样式 - 使用公司主色 */
.el-button--primary {
  background-color: #2e8b57;
  border-color: #2e8b57;
}

.el-button--primary:hover {
  background-color: #3cb371; /* 使用辅色作为悬停效果 */
  border-color: #3cb371;
}
</style>
