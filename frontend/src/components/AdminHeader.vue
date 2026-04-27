<template>
  <div class="admin-header">
    <h2 class="page-title">{{ pageTitle }}</h2>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  pageTitle: {
    type: String,
    default: '管理员控制台'
  }
})
</script>

<style scoped>
.admin-header {
  background: linear-gradient(135deg, #8DC149, #7ab838);
  color: white;
  border-bottom: 1px solid #e8eef3;
  padding: 0 30px;
  display: flex;
  align-items: center;
  height: 70px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-header {
    padding: 0 20px;
  }
}
</style>