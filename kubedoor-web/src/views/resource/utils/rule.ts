import { reactive } from "vue";
import type { FormRules } from "element-plus";
import { transformI18n } from "@/plugins/i18n";

/** 自定义表单规则校验 */
export const formRules = reactive(<FormRules>{
  namespace: [
    {
      required: true,
      message: transformI18n("resource.rules.namespace"),
      trigger: "blur"
    }
  ],
  deployment: [
    {
      required: true,
      message: transformI18n("resource.rules.deployment"),
      trigger: "blur"
    }
  ],
  pod_count_manual: [
    {
      required: true,
      message: transformI18n("resource.rules.podCountManual"),
      trigger: "blur"
    },
    {
      type: "number",
      min: -1,
      message: transformI18n("resource.rules.greaterThanZero"),
      trigger: "blur",
      transform: value => Number(value)
    }
  ],
  request_cpu_m: [
    {
      required: true,
      message: transformI18n("resource.rules.requestCpuM"),
      trigger: "blur"
    },
    {
      type: "number",
      min: -1,
      message: transformI18n("resource.rules.greaterThanZero"),
      trigger: "blur",
      transform: value => Number(value)
    }
  ],
  request_mem_mb: [
    {
      required: true,
      message: transformI18n("resource.rules.requestMemMb"),
      trigger: "blur"
    },
    {
      type: "number",
      min: -1,
      message: transformI18n("resource.rules.greaterThanZero"),
      trigger: "blur",
      transform: value => Number(value)
    }
  ],
  limit_cpu_m: [
    {
      required: true,
      message: transformI18n("resource.rules.limitCpuM"),
      trigger: "blur"
    },
    {
      type: "number",
      min: -1,
      message: transformI18n("resource.rules.greaterThanZero"),
      trigger: "blur",
      transform: value => Number(value)
    }
  ],
  limit_mem_mb: [
    {
      required: true,
      message: transformI18n("resource.rules.limitMemMb"),
      trigger: "blur"
    },
    {
      type: "number",
      min: -1,
      message: transformI18n("resource.rules.greaterThanZero"),
      trigger: "blur",
      transform: value => Number(value)
    }
  ]
});
