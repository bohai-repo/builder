<template>
  <div class="alarm-detail-container">
    <!-- 顶部区域 -->
    <div
      class="top-section mb-2"
      style="background-color: #fff; padding: 16px; border-radius: 8px"
    >
      <!-- 搜索栏 -->
      <div>
        <el-form :model="searchForm" style="margin-bottom: -18px">
          <el-row :gutter="15" style="display: flex; align-items: center">
            <!-- <el-button type="primary" plain @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button> -->

            <el-col :span="3">
              <el-form-item label="开始时间">
                <el-select
                  v-model="searchForm.timeRange"
                  placeholder="选择时间范围"
                  @change="handleTimeRangeChange"
                >
                  <el-option label="今天" :value="0" />
                  <el-option label="最近1天" :value="1" />
                  <el-option label="最近3天" :value="3" />
                  <el-option label="最近7天" :value="7" />
                  <el-option label="最近15天" :value="15" />
                  <el-option label="最近30天" :value="30" />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="3">
              <el-form-item label="K8S">
                <el-select
                  v-model="searchForm.env"
                  class="search-multi-select"
                  placeholder="请选择环境"
                  filterable
                  clearable
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  :max-collapse-tags="1"
                  @change="handleSearch"
                >
                  <el-option
                    v-for="item in envOptions"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="4">
              <el-form-item label="告警名称">
                <el-select
                  v-model="searchForm.alertName"
                  class="search-multi-select"
                  placeholder="请选择"
                  filterable
                  clearable
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  :max-collapse-tags="1"
                  @change="handleSearch"
                >
                  <el-option
                    v-for="item in alertNameOptions"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="3">
              <el-form-item label="状态">
                <el-select
                  v-model="searchForm.status"
                  placeholder="请选择"
                  clearable
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  @change="handleSearch"
                >
                  <el-option
                    v-for="option in statusOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="3">
              <el-form-item label="严重程度">
                <el-select
                  v-model="searchForm.severity"
                  placeholder="请选择"
                  clearable
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  style="width: 120px"
                  @change="handleSearch"
                >
                  <el-option
                    v-for="option in severityOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="3">
              <el-form-item label="进度">
                <el-select
                  v-model="searchForm.operate"
                  placeholder="请选择"
                  clearable
                  @change="handleSearch"
                >
                  <el-option
                    v-for="option in operateOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="4">
              <el-form-item>
                <el-tooltip
                  effect="dark"
                  :content="
                    autoRefreshInterval === 0
                      ? `自动刷新已关闭`
                      : '设置自动刷新间隔'
                  "
                  placement="top"
                >
                  <el-button-group style="margin-right: 8px">
                    <el-button type="primary" @click="handleSearch">
                      <el-icon style="margin-right: 4px"
                        ><RefreshRight
                      /></el-icon>
                      刷新
                    </el-button>
                    <el-dropdown
                      trigger="click"
                      @command="handleRefreshIntervalChange"
                    >
                      <el-button type="primary">
                        {{
                          autoRefreshInterval === 0
                            ? ""
                            : autoRefreshInterval + "s"
                        }}
                        <el-icon style="margin-left: 4px"
                          ><ArrowDown
                        /></el-icon>
                      </el-button>

                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item :command="0">关</el-dropdown-item>
                          <el-dropdown-item :command="15">15s</el-dropdown-item>
                          <el-dropdown-item :command="30">30s</el-dropdown-item>
                          <el-dropdown-item :command="60">1m</el-dropdown-item>
                          <el-dropdown-item :command="300">5m</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </el-button-group></el-tooltip
                >
                <el-button @click="handleReset">重置</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </div>

    <!-- 详情内容 -->
    <div class="content">
      <el-card v-loading="loading">
        <el-table
          :data="tableData"
          style="width: 100%"
          stripe
          @sort-change="handleSortChange"
        >
          <el-table-column
            prop="env"
            label="K8S"
            min-width="120"
            show-overflow-tooltip
          />
          <el-table-column
            prop="namespace"
            label="命名空间"
            min-width="80"
            show-overflow-tooltip
          />
          <el-table-column
            prop="pod"
            label="Pod"
            min-width="250"
            show-overflow-tooltip
          />

          <!-- 告警名称（带颜色） -->
          <el-table-column
            label="告警名称"
            min-width="200"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span :style="{ color: getSeverityColor(scope.row.severity) }">
                {{ scope.row.alert_name }}
              </span>
            </template>
          </el-table-column>

          <!-- 状态 -->
          <el-table-column
            prop="alert_status"
            label="状态"
            align="center"
            width="100"
          >
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.alert_status === 'firing' ? 'danger' : 'success'
                "
              >
                {{ scope.row.alert_status === "firing" ? "告警" : "恢复" }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 告警时间 -->
          <el-table-column
            prop="start_time"
            label="首次告警时间"
            min-width="160"
            align="center"
            sortable
          >
            <template #default="scope">
              {{ formatTime(scope.row.start_time) }}
            </template>
          </el-table-column>

          <!-- 恢复时间 -->
          <el-table-column
            prop="end_time"
            label="末次告警/恢复时间"
            min-width="180"
            align="center"
            sortable="custom"
          >
            <template #default="scope">
              <el-tooltip
                effect="dark"
                :content="
                  scope.row.alert_status === 'firing'
                    ? '末次告警时间'
                    : '恢复时间'
                "
                placement="top"
              >
                {{ scope.row.end_time ? formatTime(scope.row.end_time) : "-" }}
              </el-tooltip>
            </template>
          </el-table-column>

          <!-- 告警与恢复次数 -->
          <el-table-column
            label="告警/恢复"
            align="center"
            width="120"
            sortable="custom"
            prop="count_firing"
          >
            <template #header>
              <el-tooltip
                effect="dark"
                content="点击按告警次数排序"
                placement="top"
              >
                <span>告警/恢复</span>
              </el-tooltip>
            </template>
            <template #default="scope">
              <el-tooltip
                effect="dark"
                :content="
                  '告警次数: ' +
                  scope.row.count_firing +
                  '\n恢复次数: ' +
                  scope.row.count_resolved
                "
                placement="top"
              >
                <span>
                  <span
                    style="color: #f56c6c; font-weight: 800; font-size: 16px"
                  >
                    {{ scope.row.count_firing }}
                  </span>
                  <span style="margin: 0 4px; font-weight: 800">/</span>
                  <span
                    style="color: #67c23a; font-weight: 800; font-size: 16px"
                  >
                    {{ scope.row.count_resolved }}
                  </span>
                </span>
              </el-tooltip>
            </template>
          </el-table-column>

          <!-- 描述 -->
          <el-table-column
            prop="description"
            label="描述"
            min-width="140"
            show-overflow-tooltip
          />

          <el-table-column
            label="进度"
            props="operate"
            width="80"
            align="center"
          >
            <template #default="scope">
              <el-switch
                v-model="scope.row.operate"
                active-value="已处理"
                inactive-value="未处理"
                inline-prompt
                size="small"
                style="
                  --el-switch-on-color: #13ce66;
                  --el-switch-off-color: #ff4949;
                "
                active-text="✔"
                inactive-text="X"
                @change="val => changeOperateSwitch(val as string, scope.row)"
              />
            </template>
          </el-table-column>

          <!-- 操作栏 -->
          <el-table-column label="操作" width="90" align="center">
            <template #default="scope">
              <el-dropdown>
                <el-button type="primary" plain size="small">
                  操作
                  <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleModifyPod(scope.row)"
                      >隔离</el-dropdown-item
                    >
                    <el-dropdown-item @click="handleDeletePod(scope.row)"
                      >删除</el-dropdown-item
                    >
                    <el-dropdown-item @click="handleAutoDump(scope.row)"
                      >Dump</el-dropdown-item
                    >
                    <el-dropdown-item @click="handleAutoJstack(scope.row)"
                      >Jstack</el-dropdown-item
                    >
                    <el-dropdown-item @click="handleAutoJfr(scope.row)"
                      >JFR</el-dropdown-item
                    >
                    <el-dropdown-item @click="handleAutoJvmMem(scope.row)"
                      >JVM</el-dropdown-item
                    >
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 结果弹窗 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="操作结果"
      class="alarm-result-dialog"
      :width="
        currentOperation === 'jstack' || currentOperation === 'dump'
          ? '95%'
          : '700px'
      "
      :top="
        currentOperation === 'jstack' || currentOperation === 'dump'
          ? '2.5vh'
          : '15vh'
      "
      destroy-on-close
    >
      <pre
        class="result-content"
        :style="
          currentOperation === 'jstack' || currentOperation === 'dump'
            ? { 'max-height': '82vh', 'overflow-y': 'auto' }
            : { 'max-height': '600px', 'overflow-y': 'auto' }
        "
        v-html="resultMessage"
      />
      <template #footer>
        <el-button type="primary" @click="handleCopyAndClose">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  VideoPlay,
  VideoPause,
  Timer,
  RefreshRight
} from "@element-plus/icons-vue";
import {
  getAlarmDetail,
  getAlarmDetailTotal,
  getEnv,
  getAlertName
} from "@/api/alarm";
import dayjs from "dayjs";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowDown } from "@element-plus/icons-vue";
import {
  modifyPod,
  deletePod,
  autoDump,
  autoJstack,
  autoJfr,
  autoJvmMem,
  updateOperate
} from "@/api/alarm";
import { useSearchStoreHook } from "@/store/modules/search";

const route = useRoute();
const router = useRouter();
const searchStore = useSearchStoreHook();
const loading = ref(false);
const tableData = ref([]);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const operateOptions = [
  { label: "未处理", value: "未处理" },
  { label: "已处理", value: "已处理" }
];
const searchForm = ref({
  timeRange: route.query.timeRange ? Number(route.query.timeRange) : 0,
  env: searchStore.env
    ? [searchStore.env]
    : (route.query.env as string)
      ? [route.query.env as string]
      : [],
  alertName: (route.query.alertName as string)
    ? [route.query.alertName as string]
    : [],
  status: ["firing"],
  severity: [],
  operate: "",
  startTime: dayjs().startOf("day").format("YYYY-MM-DD HH:mm:ss")
});
const envOptions = ref([]);
const alertNameOptions = ref<string[]>([]);
const statusOptions = [
  { label: "告警", value: "firing" },
  { label: "恢复", value: "resolved" }
];
const severityOptions = [
  { label: "严重", value: "Critical" },
  { label: "警告", value: "Warning" },
  { label: "提醒", value: "Notice" },
  { label: "信息", value: "Info" }
];

// 返回上一页
const goBack = () => {
  router.back();
};

// 获取总数
const fetchTotal = async () => {
  try {
    const { data } = await getAlarmDetailTotal({
      ...searchForm.value,
      startTime: getStartTime(searchForm.value.timeRange)
    });
    if (data && data.length > 0) {
      total.value = Number(data[0][0]) || 0;
    }
  } catch (error) {
    console.error("获取总数失败:", error);
  }
};

// 根据timeRange获取startTime
const getStartTime = (timeRange: number) => {
  const now = dayjs();
  if (timeRange === 0) {
    return now.startOf("day").format("YYYY-MM-DD HH:mm:ss");
  }
  return now.subtract(timeRange, "day").format("YYYY-MM-DD HH:mm:ss");
};

// 获取详情数据
const getDetailData = async () => {
  try {
    loading.value = true;
    const { data, meta } = await getAlarmDetail({
      page: currentPage.value,
      pageSize: pageSize.value,
      ...searchForm.value,
      startTime: getStartTime(searchForm.value.timeRange)
    });
    if (data) {
      tableData.value = data.map(item => {
        let obj: any = {};
        for (let index = 0; index < meta.length; index++) {
          const key = meta[index].name;
          if (key == "operate") {
            obj[key] = item[index] == "已处理" ? "已处理" : "未处理";
          } else {
            obj[key] = item[index];
          }
          obj.index = index;
        }
        return obj;
      });
    }
  } catch (error) {
    console.error("获取告警详情失败:", error);
  } finally {
    loading.value = false;
  }
};

// 处理分页
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1; // 重置到第一页
  getDetailData();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  getDetailData();
};

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format("YYYY-MM-DD HH:mm:ss");
};

// 获取严重程度对应的颜色
const getSeverityColor = (severity: string) => {
  const map: Record<string, string> = {
    critical: "#F56C6C",
    warning: "#E6A23C",
    notice: "#409EFF",
    info: "#909399"
  };
  return map[severity.toLowerCase()] || "black";
};

// 处理时间范围变化
const handleTimeRangeChange = (val: number) => {
  searchForm.value.timeRange = val;
  handleSearch();
};

// 处理搜索
const handleSearch = async () => {
  currentPage.value = 1;
  await fetchTotal();
  getDetailData();
};

// 处理排序变化
const handleSortChange = ({
  prop,
  order
}: {
  prop: string;
  order: string | null;
}) => {
  if (prop === "end_time") {
    tableData.value.sort((a, b) => {
      const aTime = a.end_time || "-";
      const bTime = b.end_time || "-";
      if (aTime === "-" && bTime === "-") return 0;
      if (aTime === "-") return order === "ascending" ? -1 : 1;
      if (bTime === "-") return order === "ascending" ? 1 : -1;
      return order === "ascending"
        ? aTime.localeCompare(bTime)
        : bTime.localeCompare(aTime);
    });
    return;
  }
  if (prop === "count_firing") {
    tableData.value.sort((a, b) => {
      if (order === "ascending") {
        return a.count_firing - b.count_firing;
      } else if (order === "descending") {
        return b.count_firing - a.count_firing;
      }
      return 0;
    });
  }
};

// 处理重置
const handleReset = () => {
  searchForm.value = {
    timeRange: route.query.timeRange ? Number(route.query.timeRange) : 0,
    env: searchStore.env ? [searchStore.env] : [],
    alertName: (route.query.alertName as string)
      ? [route.query.alertName as string]
      : [],
    status: ["firing"],
    severity: [],
    operate: undefined,
    startTime: dayjs().startOf("day").format("YYYY-MM-DD HH:mm:ss")
  };
  handleSearch();
};

// 获取环境选项
const getEnvOptions = async () => {
  try {
    const res = await getEnv();
    envOptions.value = res.data.map((item: string[]) => item[0]);
    // 如果 store 中有值且存在于选项中，则使用 store 中的值
    if (searchStore.env && envOptions.value.includes(searchStore.env)) {
      searchForm.value.env = [searchStore.env];
    } else {
      searchForm.value.env = envOptions.value[0];
      searchStore.setEnv(envOptions.value[0]);
    }
    return Promise.resolve(envOptions.value);
  } catch (error) {
    console.error("获取环境选项失败:", error);
    return Promise.reject(error);
  }
};

// 监听环境变化
watch(
  () => searchForm.value.env,
  newVal => {
    if (newVal && newVal.length > 0) {
      searchStore.setEnv(newVal[0]);
      handleSearch();
    }
  }
);

// 获取告警名称选项
const getAlertNameOptions = async () => {
  try {
    const { data } = await getAlertName();
    if (data && data.length > 0) {
      alertNameOptions.value = data.map((item: any[]) => item[0]);
    }
  } catch (error) {
    console.error("获取告警名称失败:", error);
  }
};

const resultDialogVisible = ref(false);
const resultMessage = ref("");
const currentOperation = ref(""); // 当前操作类型

const showResultDialog = (message: string, operation: string = "") => {
  resultMessage.value = `<div style="white-space: pre-wrap; word-break: break-all;">${message}</div>`;
  currentOperation.value = operation;
  resultDialogVisible.value = true;
};

const changeOperateSwitch = async (val: string, row: any) => {
  try {
    const res = await updateOperate({
      operate: val,
      fingerprint: row.fingerprint,
      start_time: row.start_time
    });

    ElMessage.success("状态更新成功");
    // handleSearch(); // 刷新数据
  } catch (error) {
    console.error(error);
    // 用户取消或发生错误时恢复原状态
    row.operate = val === "已处理" ? "未处理" : "已处理";
    if (error !== "cancel" && error !== "close") {
      ElMessage.error("状态更新失败");
    }
  }
};

// Pod操作相关函数
const handleModifyPod = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认要隔离该Pod吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await modifyPod({
      env: row.env,
      ns: row.namespace,
      pod_name: row.pod
    });
    if (res.success) {
      ElMessage.success("操作成功");
      showResultDialog(res.message, "modify");
      handleSearch(); // 刷新数据
    } else {
      ElMessage.error("操作失败");
    }
  } catch (error) {
    console.error(error);
  }
};

const handleDeletePod = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认要删除该Pod吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await deletePod({
      env: row.env,
      ns: row.namespace,
      pod_name: row.pod
    });
    if (res.success) {
      ElMessage.success("操作成功");
      handleSearch(); // 刷新数据
    } else {
      ElMessage.error("操作失败");
    }
  } catch (error) {
    console.error(error);
  }
};

const handleAutoDump = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行Dump吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoDump({
      env: row.env,
      ns: row.namespace,
      pod_name: row.pod
    });
    if (res.success) {
      showResultDialog(res.message, "dump");
      ElMessage.success("操作成功");
    } else {
      ElMessage.error("操作失败");
    }
  } catch (error) {
    console.error(error);
  }
};

const handleAutoJstack = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行Jstack吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoJstack({
      env: row.env,
      ns: row.namespace,
      pod_name: row.pod
    });
    if (res.success) {
      showResultDialog(res.message, "jstack");
      ElMessage.success("操作成功");
    } else {
      ElMessage.error("操作失败");
    }
  } catch (error) {
    console.error(error);
  }
};

const handleAutoJfr = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行JFR吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoJfr({
      env: row.env,
      ns: row.namespace,
      pod_name: row.pod
    });
    if (res.success) {
      showResultDialog(res.message, "jfr");
      ElMessage.success("操作成功");
    } else {
      ElMessage.error("操作失败");
    }
  } catch (error) {
    console.error(error);
  }
};

const handleAutoJvmMem = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行JVM吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoJvmMem({
      env: row.env,
      ns: row.namespace,
      pod_name: row.pod
    });
    if (res.success) {
      showResultDialog(res.message, "jvm");
      ElMessage.success("操作成功");
    } else {
      ElMessage.error("操作失败");
    }
  } catch (error) {
    console.error(error);
  }
};

const handleCopyAndClose = () => {
  resultDialogVisible.value = false;
  // try {
  //   // 移除HTML标签，只复制纯文本
  //   const tempDiv = document.createElement("div");
  //   tempDiv.innerHTML = resultMessage.value;
  //   const textContent = tempDiv.textContent || tempDiv.innerText;
  //   await navigator.clipboard.writeText(textContent);
  //   ElMessage.success("复制成功");
  // } catch (err) {
  //   ElMessage.error("复制失败");
  //   console.error("复制失败:", err);
  // }
};

// 自动刷新相关
const autoRefreshInterval = ref(0); // 默认15秒
let refreshTimer: ReturnType<typeof setInterval> | null = null;

// 开始自动刷新
const startAutoRefresh = () => {
  stopAutoRefresh(); // 先清除可能存在的定时器
  refreshTimer = setInterval(() => {
    handleSearch();
  }, autoRefreshInterval.value * 1000);
};

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
};

// 处理刷新间隔变化
const handleRefreshIntervalChange = (interval: number) => {
  autoRefreshInterval.value = interval;
  if (autoRefreshInterval.value) {
    startAutoRefresh(); // 重启定时器以应用新间隔
  } else {
    stopAutoRefresh();
  }
};

onMounted(() => {
  getEnvOptions();
  getAlertNameOptions();
  handleSearch();
});

onUnmounted(() => {
  stopAutoRefresh(); // 组件卸载时清除定时器
});
</script>

<style>
.search-multi-select {
  .el-select__input-wrapper {
    display: none;
  }
}
</style>

<style>
.alarm-result-dialog {
  .result-content {
    margin: 0;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
    font-family: monospace;
    overflow-y: auto;
  }
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.content {
  background-color: #fff;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* :deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
  --el-table-border: 1px solid var(--el-table-border-color);
}

:deep(.el-table .cell) {
  white-space: pre-line;
  line-height: 1.5;
} */

.description-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}
</style>
