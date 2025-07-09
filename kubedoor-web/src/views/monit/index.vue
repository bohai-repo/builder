<template>
  <div class="realtime-monitor-container">
    <!-- 搜索表单 -->
    <div class="search-section">
      <el-form :model="searchForm" inline style="margin-bottom: -18px">
        <el-form-item label="K8S">
          <el-select
            v-model="searchForm.env"
            placeholder="请选择K8S环境"
            class="!w-[180px]"
            filterable
            @change="handleEnvChange"
          >
            <el-option
              v-for="item in envOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="命名空间">
          <el-select
            v-model="searchForm.ns"
            placeholder="请选择命名空间"
            class="!w-[180px]"
            filterable
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="item in nsOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关键字">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入关键字"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :disabled="!searchForm.env"
            @click="handleSearch"
          >
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格数据 -->
    <!-- 更新弹窗 -->
    <el-dialog v-model="updateDialogVisible" title="更新镜像" width="500px">
      <el-form :model="updateForm" label-width="80px">
        <el-form-item label="镜像标签">
          <el-input
            v-model="updateForm.imageTag"
            placeholder="请输入镜像标签"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="updateLoading"
            @click="handleUpdate"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <div class="mt-2">
      <el-card v-loading="loading">
        <el-table
          class="hide-expand"
          :data="filteredTableData"
          style="width: 100%"
          stripe
          border
          :default-sort="{ prop: 'podCount', order: 'descending' }"
          row-key="id"
          :expand-row-keys="expandedRowKeys"
        >
          <el-table-column
            prop="env"
            label="K8S"
            min-width="100"
            show-overflow-tooltip
          />
          <el-table-column
            prop="namespace"
            label="命名空间"
            min-width="80"
            show-overflow-tooltip
          />
          <el-table-column
            prop="deployment"
            label="微服务"
            min-width="140"
            show-overflow-tooltip
          />
          <el-table-column
            prop="podCount"
            label="POD"
            min-width="80"
            align="center"
            sortable
          >
            <template #header>
              <span style="color: #409eff">POD</span>
            </template>
            <template #default="scope">
              <span style="color: #409eff; font-weight: bold">{{
                scope.row.podCount
              }}</span>
            </template>
          </el-table-column>

          <el-table-column label="明细" min-width="80" align="center">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                plain
                @click.stop="handlePodDetail(scope.row)"
              >
                明细
              </el-button>
            </template>
          </el-table-column>

          <el-table-column type="expand" width="1">
            <template #default="scope">
              <div
                v-loading="scope.row.podsLoading"
                class="pod-detail-container"
              >
                <el-table
                  v-if="scope.row.pods && scope.row.pods.length > 0"
                  :data="scope.row.pods"
                  border
                  style="width: 100%"
                >
                  <el-table-column
                    prop="name"
                    label="名称"
                    min-width="200"
                    show-overflow-tooltip
                    align="center"
                  >
                    <template #default="podScope">
                      <div
                        style="
                          direction: rtl;
                          text-align: left;
                          overflow: hidden;
                          text-overflow: ellipsis;
                          white-space: nowrap;
                        "
                      >
                        {{ podScope.row.name }}
                      </div>
                    </template>
                  </el-table-column>

                  <el-table-column
                    prop="status"
                    label="状态"
                    min-width="80"
                    align="center"
                  >
                    <template #default="podScope">
                      <el-tag
                        :type="
                          podScope.row.status === 'Running'
                            ? 'success'
                            : 'danger'
                        "
                      >
                        {{ podScope.row.status }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column
                    prop="ready"
                    label="就绪"
                    min-width="60"
                    align="center"
                  >
                    <template #default="podScope">
                      <el-tag
                        :type="podScope.row.ready ? 'success' : 'warning'"
                      >
                        {{ podScope.row.ready ? "是" : "否" }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column
                    prop="pod_ip"
                    label="Pod IP"
                    min-width="120"
                    align="center"
                    show-overflow-tooltip
                  />
                  <el-table-column
                    prop="cpu"
                    label="CPU"
                    min-width="80"
                    align="center"
                    sortable
                  />
                  <el-table-column
                    prop="memory"
                    label="内存"
                    min-width="80"
                    align="center"
                    sortable
                  />
                  <el-table-column
                    prop="created_at"
                    label="创建时间"
                    min-width="160"
                    align="center"
                    sortable
                  />
                  <el-table-column
                    prop="node_name"
                    label="节点名称"
                    min-width="110"
                    show-overflow-tooltip
                    align="center"
                    sortable
                  />
                  <el-table-column
                    prop="app_label"
                    label="应用标签"
                    min-width="150"
                    align="center"
                    show-overflow-tooltip
                    sortable
                  >
                    <template #default="podScope">
                      <div
                        style="
                          direction: rtl;
                          text-align: left;
                          overflow: hidden;
                          text-overflow: ellipsis;
                          white-space: nowrap;
                        "
                      >
                        {{ podScope.row.app_label }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column
                    prop="image"
                    label="镜像标签"
                    min-width="300"
                    show-overflow-tooltip
                    align="center"
                    sortable
                  >
                    <template #default="podScope">
                      <div
                        style="
                          direction: rtl;
                          text-align: left;
                          overflow: hidden;
                          text-overflow: ellipsis;
                          white-space: nowrap;
                        "
                      >
                        {{ podScope.row.image }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column
                    prop="restart_count"
                    label="重启"
                    min-width="60"
                    align="center"
                  />
                  <el-table-column
                    prop="restart_reason"
                    label="重启原因"
                    min-width="130"
                    align="center"
                    show-overflow-tooltip
                  />
                  <el-table-column
                    prop="exception_reason"
                    label="异常状态原因"
                    min-width="150"
                    show-overflow-tooltip
                  />
                  <el-table-column
                    label="操作"
                    width="80"
                    align="center"
                    fixed="right"
                  >
                    <template #default="podScope">
                      <el-dropdown>
                        <el-button type="primary" size="small">
                          操作
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item
                              @click="
                                handleModifyPod(
                                  scope.row.env,
                                  scope.row.namespace,
                                  podScope.row.name
                                )
                              "
                              >隔离</el-dropdown-item
                            >
                            <el-dropdown-item
                              @click="
                                handleDeletePod(
                                  scope.row.env,
                                  scope.row.namespace,
                                  podScope.row.name
                                )
                              "
                              >删除</el-dropdown-item
                            >
                            <el-dropdown-item
                              @click="
                                handleAutoDump(
                                  scope.row.env,
                                  scope.row.namespace,
                                  podScope.row.name
                                )
                              "
                              >Dump</el-dropdown-item
                            >
                            <el-dropdown-item
                              @click="
                                handleAutoJstack(
                                  scope.row.env,
                                  scope.row.namespace,
                                  podScope.row.name
                                )
                              "
                              >Jstack</el-dropdown-item
                            >
                            <el-dropdown-item
                              @click="
                                handleAutoJfr(
                                  scope.row.env,
                                  scope.row.namespace,
                                  podScope.row.name
                                )
                              "
                              >JFR</el-dropdown-item
                            >
                            <el-dropdown-item
                              @click="
                                handleAutoJvmMem(
                                  scope.row.env,
                                  scope.row.namespace,
                                  podScope.row.name
                                )
                              "
                              >JVM</el-dropdown-item
                            >
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </template>
                  </el-table-column>
                </el-table>
                <div v-else-if="!scope.row.podsLoading" class="no-data">
                  暂无Pod数据
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            prop="avgCpu"
            label="平均CPU"
            min-width="110"
            align="center"
            sortable
          >
            <template #default="scope"> {{ scope.row.avgCpu }}m </template>
          </el-table-column>
          <el-table-column
            prop="maxCpu"
            label="最大CPU"
            min-width="110"
            align="center"
            sortable
          >
            <template #header>
              <span style="color: #f56c6c">最大CPU</span>
            </template>
            <template #default="scope">
              <span style="color: #f56c6c; font-weight: bold"
                >{{ scope.row.maxCpu }}m</span
              >
            </template>
          </el-table-column>
          <el-table-column
            prop="requestCpu"
            label="需求CPU"
            min-width="110"
            align="center"
            sortable
          >
            <template #default="scope"> {{ scope.row.requestCpu }}m </template>
          </el-table-column>
          <el-table-column
            prop="limitCpu"
            label="限制CPU"
            min-width="110"
            align="center"
            sortable
          >
            <template #header>
              <span style="color: #409eff">限制CPU</span>
            </template>
            <template #default="scope">
              <span style="color: #409eff; font-weight: bold"
                >{{ scope.row.limitCpu }}m</span
              >
            </template>
          </el-table-column>
          <el-table-column
            prop="avgMem"
            label="平均MEM"
            min-width="110"
            align="center"
            sortable
          >
            <template #default="scope"> {{ scope.row.avgMem }}MB </template>
          </el-table-column>

          <el-table-column
            prop="maxMem"
            label="最大MEM"
            min-width="110"
            align="center"
            sortable
          >
            <template #header>
              <span style="color: #f56c6c">最大MEM</span>
            </template>
            <template #default="scope">
              <span style="color: #f56c6c; font-weight: bold"
                >{{ scope.row.maxMem }}MB</span
              >
            </template>
          </el-table-column>

          <el-table-column
            prop="requestMem"
            label="需求MEM"
            min-width="110"
            align="center"
            sortable
          >
            <template #default="scope"> {{ scope.row.requestMem }}MB </template>
          </el-table-column>

          <el-table-column
            prop="limitMem"
            label="限制MEM"
            min-width="110"
            align="center"
            sortable
          >
            <template #header>
              <span style="color: #409eff">限制MEM</span>
            </template>
            <template #default="scope">
              <span style="color: #409eff; font-weight: bold">
                {{ scope.row.limitMem }}MB
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="80" align="center">
            <template #default="scope">
              <el-dropdown>
                <el-button type="primary" size="small" plain>
                  操作
                  <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleCapacity(scope.row)"
                      >扩缩容</el-dropdown-item
                    >
                    <el-dropdown-item @click="onReboot(scope.row)"
                      >重启</el-dropdown-item
                    >
                    <el-dropdown-item @click="openUpdateDialog(scope.row)"
                      >更新</el-dropdown-item
                    >
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
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
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import {
  modifyPod,
  deletePod,
  autoDump,
  autoJstack,
  autoJfr,
  autoJvmMem,
  updateOperate
} from "@/api/alarm";
import { ArrowDown } from "@element-plus/icons-vue";
import {
  getPromEnv,
  getPromNamespace,
  getPromQueryData,
  getPodData
} from "@/api/monit";
import { useResource } from "./utils/hook";
import { useSearchStoreHook } from "@/store/modules/search";

const { onChangeCapacity, onReboot, onUpdateImage } = useResource();
const searchStore = useSearchStoreHook();

// 定义表单数据
const searchForm = reactive({
  env: searchStore.env,
  ns: searchStore.namespace,
  keyword: ""
});

// 定义选项数据
const envOptions = ref<string[]>([]);
const nsOptions = ref<string[]>([]);

// 表格数据
const tableData = ref<any[]>([]);
const filteredTableData = ref<any[]>([]);
// const filteredTableData = computed(() => {
//   if (!searchForm.keyword) {
//     return tableData.value;
//   }

//   const keyword = searchForm.keyword.toLowerCase();
//   return tableData.value.filter(
//     item =>
//       item.env.toLowerCase().includes(keyword) ||
//       (item.namespace && item.namespace.toLowerCase().includes(keyword)) ||
//       (item.deployment && item.deployment.toLowerCase().includes(keyword))
//   );
// });

// 展开行相关
const expandedRowKeys = ref<string[]>([]);

// 处理Pod详情
const handlePodDetail = async (row: any) => {
  // 如果已经加载过Pod数据，直接展开/收起行
  if (expandedRowKeys.value.includes(row.id)) {
    expandedRowKeys.value = expandedRowKeys.value.filter(id => id !== row.id);
    return;
  }

  // 设置唯一ID用于展开行
  if (!row.id) {
    row.id = `${row.env}-${row.namespace}-${row.deployment}`;
  }

  // 设置加载状态
  row.podsLoading = true;

  try {
    const res = await getPodData(row.env, row.namespace, row.deployment);
    if (res.pods) {
      row.pods = res.pods;
    } else {
      row.pods = [];
    }
    // 展开行
    expandedRowKeys.value.push(row.id);
  } catch (error) {
    console.error("获取Pod数据失败:", error);
    ElMessage.error("获取Pod数据失败");
    row.pods = [];
  } finally {
    row.podsLoading = false;
  }
};

// 加载状态
const loading = ref(false);

// 更新弹窗相关
const updateDialogVisible = ref(false);
const updateLoading = ref(false);
const selectedDeployment = ref<any>(null);
const updateForm = reactive({
  imageTag: ""
});

const openUpdateDialog = (row: any) => {
  selectedDeployment.value = row;
  updateForm.imageTag = "";
  updateDialogVisible.value = true;
};

const handleUpdate = async () => {
  if (!updateForm.imageTag) {
    ElMessage.warning("请输入镜像标签");
    return;
  }

  updateLoading.value = true;
  try {
    await onUpdateImage(selectedDeployment.value.env, {
      deployment: selectedDeployment.value.deployment,
      namespace: selectedDeployment.value.namespace,
      image_tag: updateForm.imageTag
    });
    updateDialogVisible.value = false;
    handleSearch();
  } finally {
    updateLoading.value = false;
  }
};

// 获取K8S环境列表
const getEnvOptions = async (): Promise<void> => {
  try {
    const res = await getPromEnv();
    if (res.data && res.data.length > 0) {
      envOptions.value = res.data.map(item => item);
      // 如果 store 中有值且存在于选项中，则使用 store 中的值
      if (searchStore.env && envOptions.value.includes(searchStore.env)) {
        searchForm.env = searchStore.env;
        await getNsOptions(searchStore.env);
      } else {
        searchForm.env = res.data[0];
        await getNsOptions(res.data[0]);
      }
    }
    return Promise.resolve();
  } catch (error) {
    console.error("获取K8S环境列表失败:", error);
    ElMessage.error("获取K8S环境列表失败");
    return Promise.reject(error);
  }
};

// 处理环境变化
const handleEnvChange = async (val: string) => {
  searchForm.ns = "";
  searchStore.setEnv(val);
  if (val) {
    await getNsOptions(val);
    handleSearch();
  } else {
    tableData.value = [];
  }
};

// 获取命名空间列表
const getNsOptions = async (env: string): Promise<void> => {
  if (!env) {
    nsOptions.value = [];
    return Promise.resolve();
  }

  try {
    const res = await getPromNamespace(env);
    if (res.data) {
      nsOptions.value = res.data.map(item => item);
      if (
        searchStore.namespace &&
        nsOptions.value.includes(searchStore.namespace)
      ) {
        searchForm.ns = searchStore.namespace;
      } else {
        searchForm.ns = res.data[0];
        searchStore.setNamespace(res.data[0]);
      }
    }
    return Promise.resolve();
  } catch (error) {
    console.error("获取命名空间列表失败:", error);
    ElMessage.error("获取命名空间列表失败");
    return Promise.reject(error);
  }
};

// 处理搜索
const handleSearch = async () => {
  if (!searchForm.env) {
    ElMessage.warning("请选择K8S环境");
    return;
  }
  searchStore.setNamespace(searchForm.ns);

  loading.value = true;
  try {
    const res = await getPromQueryData(searchForm.env, searchForm.ns);
    if (res.data) {
      tableData.value = res.data.map(item => {
        const env = item[0] || "-";
        const namespace = item[1] || "-";
        const deployment = item[2] || "-";

        return {
          id: `${env}-${namespace}-${deployment}`,
          env,
          namespace,
          deployment,
          podCount: item[3] || 0,
          avgCpu: item[4] ? Math.round(item[4]) : 0,
          maxCpu: item[5] ? Math.round(item[5]) : 0,
          requestCpu: item[6] ? Math.round(item[6]) : 0,
          limitCpu: item[7] ? Math.round(item[7]) : 0,
          avgMem: item[8] ? Math.round(item[8]) : 0,
          maxMem: item[9] ? Math.round(item[9]) : 0,
          requestMem: item[10] ? Math.round(item[10]) : 0,
          limitMem: item[11] ? Math.round(item[11]) : 0,
          pods: [],
          podsLoading: false
        };
      });
    } else {
      tableData.value = [];
    }

    const keyword = searchForm.keyword.toLowerCase();

    if (!searchForm.keyword) {
      filteredTableData.value = tableData.value;
    } else {
      filteredTableData.value = tableData.value.filter(
        item =>
          item.env.toLowerCase().includes(keyword) ||
          (item.namespace && item.namespace.toLowerCase().includes(keyword)) ||
          (item.deployment && item.deployment.toLowerCase().includes(keyword))
      );
    }
  } catch (error) {
    console.error("获取监控数据失败:", error);
    ElMessage.error("获取监控数据失败");
    tableData.value = [];
  } finally {
    loading.value = false;
  }
};

// 处理重置
const handleReset = async () => {
  searchForm.env = envOptions.value[0] || "";
  searchForm.keyword = "";
  searchStore.clearStorage();
  await handleEnvChange(envOptions.value[0]);
};

const handleCapacity = async (row: any) => {
  await onChangeCapacity(row);
  // handleSearch();
};

const resultDialogVisible = ref(false);
const resultMessage = ref("");
const currentOperation = ref(""); // 当前操作类型

const showResultDialog = (message: string, operation: string = "") => {
  resultMessage.value = `<div style="white-space: pre-wrap; word-break: break-all;">${message}</div>`;
  currentOperation.value = operation;
  resultDialogVisible.value = true;
};

// Pod操作相关函数
const handleModifyPod = async (env: string, namespace: string, pod: string) => {
  try {
    await ElMessageBox.confirm("确认要隔离该Pod吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await modifyPod({
      env: env,
      ns: namespace,
      pod_name: pod
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

const handleDeletePod = async (env: string, namespace: string, pod: string) => {
  try {
    await ElMessageBox.confirm("确认要删除该Pod吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await deletePod({
      env: env,
      ns: namespace,
      pod_name: pod
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

const handleAutoDump = async (env: string, namespace: string, pod: string) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行Dump吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoDump({
      env: env,
      ns: namespace,
      pod_name: pod
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

const handleAutoJstack = async (
  env: string,
  namespace: string,
  pod: string
) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行Jstack吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoJstack({
      env: env,
      ns: namespace,
      pod_name: pod
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

const handleAutoJfr = async (env: string, namespace: string, pod: string) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行JFR吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoJfr({
      env: env,
      ns: namespace,
      pod_name: pod
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

const handleAutoJvmMem = async (
  env: string,
  namespace: string,
  pod: string
) => {
  try {
    await ElMessageBox.confirm("确认要对该Pod执行JVM吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    const res = await autoJvmMem({
      env: env,
      ns: namespace,
      pod_name: pod
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

// 页面加载时获取环境列表
onMounted(async () => {
  await getEnvOptions();
  // 如果已经有环境值，则执行搜索
  if (searchForm.env) {
    handleSearch();
  }
});
</script>

<style scoped>
.search-section {
  background-color: #fff;
  padding: 16px;
  border-radius: 8px;
}

.el-form-item {
  margin-bottom: 18px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.pod-detail-container {
  padding: 5px;
  background-color: #f5f7fa;
  border-radius: 0px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px 0;
  font-size: 14px;
}
</style>

<style>
.hide-expand {
  .el-table__expand-icon {
    display: none;
  }
}
</style>
