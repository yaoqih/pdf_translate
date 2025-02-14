<template>
  <el-container class="admin-layout">
    <el-aside width="200px">
      <el-menu
        router
        :default-active="$route.path"
        class="admin-menu"
      >
        <el-menu-item index="/admin/keys">
          <el-icon><key /></el-icon>
          <span>密钥管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/files">
          <el-icon><document /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/statistics">
          <el-icon><data-line /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header height="60px">
        <div class="header-content">
          <h2>PDF翻译服务管理系统</h2>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-layout {
  height: 100vh;
}

.admin-menu {
  height: 100%;
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style> 