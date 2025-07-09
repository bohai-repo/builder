<script setup lang="ts">
import { ref } from "vue";
type Props = {
  isKunlun: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  isKunlun: true
});

const newIsKunlun = ref(props.isKunlun);

function getEnv() {
  return newIsKunlun.value;
}

defineExpose({ getEnv });
</script>

<template>
  <div>
    <el-switch
      v-model="newIsKunlun"
      size="large"
      inline-prompt
      style="--el-switch-on-color: #4169e1; --el-switch-off-color: #ff8c00"
      active-text="昆仑"
      inactive-text="蓬莱"
    />
  </div>
</template>
