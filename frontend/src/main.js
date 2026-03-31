// 从 vue 中引入 createApp（创建 Vue 应用用的）
import { createApp } from 'vue'

// 引入根组件 App.vue
import App from './App.vue'

import './style.css'

// 引入 Element Plus UI 库
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入 Element Plus 图标库
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入路由配置
import router from './router'

// 创建 Vue 应用实例
const app = createApp(App)

// 使用 Element Plus
app.use(ElementPlus)

// 全局注册 Element Plus 图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用路由
app.use(router)

// 把整个 Vue 应用挂载到 index.html 的 #app 上
app.mount('#app')

