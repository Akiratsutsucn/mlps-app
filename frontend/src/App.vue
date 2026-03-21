<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <el-container style="min-height: 100vh">
    <el-header style="background: #1d3557; display: flex; align-items: center; justify-content: space-between;">
      <div style="display: flex; align-items: center; cursor: pointer;" @click="router.push('/')">
        <el-icon :size="24" color="#fff" style="margin-right: 10px;"><Shield /></el-icon>
        <span style="color: #fff; font-size: 18px; font-weight: bold;">等级保护评测过程记录系统</span>
      </div>
      <el-menu mode="horizontal" background-color="#1d3557" text-color="#a8dadc" active-text-color="#f1faee" :ellipsis="false" router style="border: none;">
        <el-menu-item index="/">项目管理</el-menu-item>
        <el-menu-item index="/question-bank">题库管理</el-menu-item>
      </el-menu>
    </el-header>
    <el-main style="background: #f5f5f5; padding: 20px;">
      <router-view />
    </el-main>
  </el-container>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
.el-header { padding: 0 20px; }
</style>
