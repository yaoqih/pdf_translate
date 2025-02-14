  <!-- 密钥信息 -->
  <el-descriptions v-if="keyInfo" :column="3" class="mt-4">
    <el-descriptions-item label="密钥">{{ keyInfo.key }}</el-descriptions-item>
    <el-descriptions-item label="剩余页数">{{ keyInfo.page_count }}</el-descriptions-item>
    <el-descriptions-item label="已使用页数">{{ keyInfo.used_count || 0 }}</el-descriptions-item>
    <el-descriptions-item label="总页数">{{ keyInfo.total_pages }}</el-descriptions-item>
    <el-descriptions-item label="状态">
      <el-tag :type="keyInfo.is_active ? 'success' : 'danger'">
        {{ keyInfo.is_active ? '有效' : '无效' }}
      </el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="过期时间">{{ formatDate(keyInfo.expired_at) }}</el-descriptions-item>
  </el-descriptions> 