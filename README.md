# AI冠军教练

企业级在线学习培训管理系统，支持用户管理、文件上传下载、学习进度跟踪、题库管理、考试系统等功能。

## 项目简介

AI冠军教练是一套面向企业的在线学习培训平台，采用前后端分离架构，提供完善的用户管理、学习内容管理、题库管理和考试系统功能。

## 技术栈

### 前端
- Vue 3 + Vite
- Vue Router 4
- Element Plus
- Axios

### 后端
- FastAPI
- PyMySQL
- PyJWT
- Python-dotenv

## 项目结构

```
ai_champion_coach/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── user.py     # 用户管理
│   │   │   ├── train.py    # 培训管理
│   │   │   ├── ai.py       # AI服务
│   │   │   ├── exam.py     # 考试管理
│   │   │   ├── upload.py   # 文件上传
│   │   │   └── question.py # 题库管理
│   │   └── core/
│   │       └── db.py       # 数据库连接
│   ├── uploads/            # 上传文件目录
│   ├── utils/
│   │   └── jwt.py          # JWT工具
│   └── main.py             # 应用入口
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/            # API接口封装
│   │   ├── components/     # 公共组件
│   │   ├── router/         # 路由配置
│   │   ├── views/          # 页面组件
│   │   └── assets/         # 静态资源
│   └── package.json
└── ai_coach_service/       # AI服务模块
```

## 功能模块

### 1. 用户管理
- 用户登录/登出
- 管理员与员工角色区分
- 用户信息管理
- 角色权限控制（0-管理员，1-商铺开发，2-上门服务，3-品牌开发，4-商铺招商，5-品牌选址）

### 2. 文件管理
- 支持多种文件格式上传（文档、图片、视频、音频等）
- 文件分类管理（技术文档、培训资料、其他）
- 文件下载功能

### 3. 学习中心
- 学习内容展示与阅读
- 学习进度跟踪
- 学习时间统计
- 个人中心学习记录展示

### 4. 题库管理
- 题目类型：单选题、多选题、判断题
- 题目分类：通用(0)、商铺开发(1)、品牌开发(2)、品牌选址(3)、上门服务(4)、商铺招商(5)
- 难易程度：简单、中等、困难
- 完整CRUD操作
- 题目筛选功能（按类型和分类）

### 5. 学习情况统计
- 用户学习进度查看
- 学习时长统计
- 完成状态追踪

### 6. 评估中心
- 模拟测试：根据用户角色筛选题目，通用题目所有角色可见
- 正式考试：随机获取题目（多选5题、单选10题、判断10题）
- 防作弊机制：切屏弹窗提醒（三次后自动交卷）
- 倒计时结束自动提交
- 页面关闭/切换自动交卷
- 返回按钮确认退出

### 7. 考试安全机制
- 后端校验答案并计算分数
- 防止前端篡改分数
- 统计数据（正确数、错误数、正确率）后端计算

### 8. 成绩管理
- 历史成绩查询
- 错题详情查看（功能开发中）
- 员工成绩统计（管理员专用）
- 考试记录展示

## 环境配置

### 后端配置 (.env)

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=champion_coach

SECRET_KEY=your_secret_key
ALGORITHM=HS256
EXPIRE_MINUTES=1440
```

## 运行项目

### 1. 数据库初始化

```bash
mysql -u root -p < champion_coach.sql
```

### 2. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问项目

前端地址：http://localhost:5173
后端API：http://localhost:8001

## 默认账号

| 角色   | 用户名 | 密码  | 角色值 |
|--------|--------|-------|--------|
| 管理员 | admin  | admin | 0      |
| 员工   | user   | user  | 1      |

## API接口

### 用户相关
- `POST /login` - 用户登录
- `GET /user/info` - 获取用户信息
- `POST /logout` - 用户登出

### 文件相关
- `POST /upload/file` - 上传文件
- `GET /upload/list` - 获取文件列表
- `GET /upload/download/{file_id}` - 下载文件

### 题库相关
- `GET /question/list` - 获取题目列表
- `GET /question/{id}` - 获取单个题目
- `POST /question/add` - 添加题目
- `POST /question/update/{id}` - 更新题目
- `POST /question/delete/{id}` - 删除题目

### 学习相关
- `GET /train/content` - 获取学习内容
- `POST /progress/update` - 更新学习进度
- `GET /learning/status` - 获取学习情况统计

### 考试相关
- `GET /exam/random_questions` - 获取随机题目
- `POST /exam/submit_answer` - 提交答案（后端评分）
- `POST /exam/save_result` - 保存考试结果
- `GET /exam/history` - 获取历史成绩
- `GET /exam/all_exam_results` - 获取所有员工成绩（管理员）

## 开发说明

### 前端开发
```bash
# 代码规范检查
npm run build

# 预览生产构建
npm run preview
```

### 后端开发
```bash
# 激活虚拟环境（可选）
conda activate kefu

# 运行后端（开发模式）
uvicorn main:app --reload
```

## 注意事项

1. 上传文件大小限制需在后端配置中调整
2. 数据库连接信息需与环境一致
3. CORS已配置本地开发地址，如需远程访问请修改 `main.py` 中的 `allow_origins`
4. 考试系统已修复安全问题，所有分数计算均在后端完成

## 最近更新

### 核心功能优化
- ✅ 题库分类字段类型修改：`category` 字段从字符串改为数字类型（0-5）
- ✅ 考试安全修复：后端校验答案并计算分数，防止前端篡改
- ✅ 防作弊机制：切屏提醒、倒计时自动提交、页面关闭自动交卷
- ✅ 评估中心模拟测试：按角色筛选题目
- ✅ 正式考试：随机获取题目，支持多选、单选、判断题
- ✅ 管理员员工成绩页面：展示所有员工考试成绩

### 性能优化
- ✅ 并行加载优化：用户信息与历史记录并行加载
- ✅ 路由守卫：防止返回正式考试页面

### Bug修复
- ✅ 修复 `get_all_exam_results` 接口数据库字段错误
- ✅ 修复登出功能不完善问题
- ✅ 修复考试结果保存问题
