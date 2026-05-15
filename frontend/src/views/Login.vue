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

        <!-- 角色选择 -->
        <el-form-item class="role-selection">
          <div class="role-buttons">
            <div 
              class="role-button" 
              :class="{ active: form.role === 'admin' }"
              @click="form.role = 'admin'"
            >
              <div class="role-avatar admin-avatar">
                <el-icon><Setting /></el-icon>
              </div>
              <div class="role-info">
                <h3 class="role-name">管理员</h3>
                <p class="role-description">管理系统用户和设置</p>
              </div>
              <el-radio v-model="form.role" value="admin" class="role-radio"></el-radio>
            </div>
            <div 
              class="role-button" 
              :class="{ active: form.role === 'employee' }"
              @click="form.role = 'employee'"
            >
              <div class="role-avatar employee-avatar">
                <el-icon><User /></el-icon>
              </div>
              <div class="role-info">
                <h3 class="role-name">员工</h3>
                <p class="role-description">使用系统进行日常工作</p>
              </div>
              <el-radio v-model="form.role" value="employee" class="role-radio"></el-radio>
            </div>
          </div>
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
  password: '',
  role: 'employee' // 默认选择员工角色
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
    console.log('选择角色：', form.role)
    console.log('登录返回完整对象：', res)
    console.log('登录返回对象的键：', Object.keys(res))
    console.log('登录返回的role字段：', res.role)

    if (res.success) {
      ElMessage.success('登录成功')

      //保存登录态（token）
      localStorage.setItem('token', res.token)
      
      // 保存用户角色
      if (res.role) {
        localStorage.setItem('userRole', res.role)
      }

      // 尝试从token中解析role信息
      let userRole = res.role;
      if (!userRole && res.token) {
        try {
          const tokenPayload = JSON.parse(atob(res.token.split('.')[1]));
          userRole = tokenPayload.role;
          console.log('从token中解析出的role:', userRole);
        } catch (e) {
          console.error('解析token失败:', e);
        }
      }
      
      // 根据角色和权限跳转到相应页面
      // 数据库中 role 是数字类型：0=管理员，1-5=其他角色
      if (form.role === 'admin' && (userRole === 'admin' || userRole === '管理员' || userRole === 0)) {
        // 管理员角色且权限验证通过，跳转到管理员界面
        router.push('/admin')
      } else {
        // 员工角色或管理员权限验证失败，跳转到现有首页
        router.push('/dashboard')
      }
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

/* 角色选择样式 */
.role-selection {
  margin-bottom: 30px;
}

.role-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: stretch;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.role-button {
  position: relative;
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background-color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 180px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  height: 100%;
}

.role-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border-color: #34d399;
}

.role-button.active {
  border-color: #2e8b57;
  background-color: rgba(46, 139, 87, 0.05);
  box-shadow: 0 4px 12px rgba(46, 139, 87, 0.15);
}

.role-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
  color: #ffffff;
}

.admin-avatar {
  background-color: #41e0c1;
}

.employee-avatar {
  background-color: #bce046;
}

.role-info {
  flex: 1;
}

.role-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.role-description {
  margin: 0;
  font-size: 11px;
  color: #6b7280;
  line-height: 1.3;
}

.role-radio {
  position: absolute;
  top: 16px;
  right: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .role-buttons {
    flex-direction: row;
    flex-wrap: nowrap;
    gap: 10px;
  }
  
  .role-button {
    padding: 15px;
    min-width: 140px;
  }
  
  .role-avatar {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .role-name {
    font-size: 16px;
  }
  
  .role-description {
    font-size: 12px;
  }
}

/* 小屏幕适配 */
@media (max-width: 480px) {
  .role-buttons {
    gap: 8px;
  }
  
  .role-button {
    padding: 12px;
    min-width: 120px;
  }
  
  .role-avatar {
    width: 40px;
    height: 40px;
    font-size: 16px;
    margin-right: 10px;
  }
  
  .role-name {
    font-size: 14px;
  }
  
  .role-description {
    font-size: 10px;
  }
}
</style>
