<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessageBox } from "element-plus";
import { message } from "@/utils/message";

import { transformI18n } from "@/plugins/i18n";

import { initByDays, whSwitch } from "@/api/workbench";
import { getEnv } from "@/api/resource";

defineOptions({
  name: "Welcome"
});

const days = ref(10);
const webhookSwitch = ref(false); // webhook switch
const envList = ref([]);
const modelEnv = ref("");
const currentEnv = ref(""); // 当前环境

// 切换环境的处理函数
function handleEnvChange(val) {
  ElMessageBox.confirm(
    `${transformI18n("workbench.switchEnvConfirm")}${val}？`,
    transformI18n("panel.purePrompt"),
    {
      confirmButtonText: transformI18n("buttons.pureConfirm"),
      cancelButtonText: transformI18n("buttons.pureCancel"),
      type: "warning"
    }
  )
    .then(() => {
      modelEnv.value = val;
      currentEnv.value = val;
      getSwitchStatus();
      message(transformI18n("workbench.switchEnvSuccess"), { type: "success" });
    })
    .catch(() => {
      modelEnv.value = currentEnv.value; // 保持原值
    });
}

function handleInit() {
  if (days.value <= 0) {
    message(transformI18n("workbench.greaterThanZero"), { type: "warning" });
    return;
  }
  ElMessageBox.confirm(
    "<strong>" +
      transformI18n("workbench.confirm") +
      "( " +
      days.value +
      transformI18n("workbench.days") +
      " )" +
      "</strong>" +
      "<div><strong>" +
      transformI18n("workbench.confirm1") +
      "</strong></div>" +
      "<div><strong>" +
      transformI18n("workbench.confirm2") +
      "</strong></div>" +
      "<div><strong>" +
      transformI18n("workbench.confirm3") +
      "</strong></div>",
    transformI18n("panel.purePrompt"),
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: transformI18n("buttons.pureConfirm"),
      cancelButtonText: transformI18n("buttons.pureCancel"),
      type: "warning"
    }
  ).then(() => {
    initByDays(days.value, currentEnv.value).then(() => {
      message(transformI18n("workbench.initSuccess"), { type: "success" });
    });
  });
}

function changeSwitch(val) {
  ElMessageBox.confirm(
    val
      ? transformI18n("workbench.controlSwitchConfirmEnable")
      : transformI18n("workbench.controlSwitchConfirmDisable"),
    transformI18n("panel.purePrompt"),
    {
      confirmButtonText: transformI18n("buttons.pureConfirm"),
      cancelButtonText: transformI18n("buttons.pureCancel"),
      type: "warning"
    }
  )
    .then(() => {
      whSwitch(val ? "on" : "off", currentEnv.value)
        .then(() => {
          message(
            val
              ? transformI18n("workbench.switchEnableSuccess")
              : transformI18n("workbench.switchDisableSuccess"),
            { type: "success" }
          );
        })
        .finally(() => {
          getSwitchStatus();
        });
    })
    .catch(() => {
      webhookSwitch.value = !val;
    });
}

function getSwitchStatus() {
  whSwitch("get", currentEnv.value).then(res => {
    webhookSwitch.value = !!(res as any).is_on;
  });
}

onMounted(async () => {
  let envRes = await getEnv();
  envList.value = envRes.data;
  currentEnv.value = envList.value[0];
  modelEnv.value = envList.value[0];
  getSwitchStatus();
});
</script>

<template>
  <div>
    <el-card class="mt-4">
      <template #header>
        <div class="card-header">
          <span>{{ transformI18n("workbench.environment") }}</span>
        </div>
      </template>
      <el-row :gutter="10">
        <el-col :xs="8" :sm="8" :md="8" :lg="6">
          <el-form>
            <el-form-item
              :label="transformI18n('workbench.currentEnvironment') + ' : '"
            >
              <el-select
                v-model="modelEnv"
                width="200px"
                @change="handleEnvChange"
              >
                <el-option
                  v-for="env in envList"
                  :key="env[0]"
                  :label="env[0]"
                  :value="env[0]"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </el-col>
      </el-row>
    </el-card>
    <el-card class="mt-4">
      <template #header>
        <div class="card-header">
          <span>{{ transformI18n("workbench.init") }}</span>
        </div>
      </template>
      <el-row :gutter="10">
        <el-col :xs="8" :sm="8" :md="8" :lg="6">
          <el-form>
            <el-form-item :label="transformI18n('workbench.daysLable') + ' : '">
              <el-input
                v-model="days"
                width="200px"
                type="number"
                :placeholder="transformI18n('workbench.daysPlaceholder')"
              />
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12">
          <el-button type="primary" @click="handleInit">{{
            transformI18n("workbench.init")
          }}</el-button>
        </el-col>
      </el-row>
    </el-card>
    <el-card class="mt-4">
      <template #header>
        <div class="card-header">
          <span>{{ transformI18n("workbench.controlSwitch") }}</span>
        </div>
      </template>
      <el-row :gutter="10">
        <el-col :span="12">
          <el-form>
            <el-form-item
              :label="transformI18n('workbench.controlStatus') + ' : '"
            >
              <el-switch
                v-model="webhookSwitch"
                size="large"
                inline-prompt
                style="
                  --el-switch-on-color: #13ce66;
                  --el-switch-off-color: #ff4949;
                "
                :active-text="transformI18n('workbench.controlEnable')"
                :inactive-text="transformI18n('workbench.controlDisable')"
                @change="changeSwitch"
              />
            </el-form-item>
          </el-form>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>
