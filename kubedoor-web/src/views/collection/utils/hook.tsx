// import "./reset.css";
// import dayjs from "dayjs";
import { deviceDetection } from "@pureadmin/utils";
import { getCollection, getEnv } from "@/api/resource";
// import { ElMessageBox } from "element-plus";
import { ref, reactive, onMounted, watch } from "vue";
import { transformI18n } from "@/plugins/i18n";
import { message } from "@/utils/message";

export function useCollection(searchStore: any) {
  const queryForm = reactive({
    date: "",
    env: searchStore.env || ""
  });
  const envList = ref([]);
  const dataList = ref([]);
  const loading = ref(false);

  const columns: TableColumnList = [
    {
      label: transformI18n("resource.column.env"),
      showOverflowTooltip: true,
      prop: "env"
    },
    // {
    //   label: transformI18n("resource.column.envPct"),
    //   prop: "env_pct",
    //   formatter: ({ env_pct }) => env_pct.toFixed(2) + "%"
    // },
    {
      label: transformI18n("resource.column.namespace"),
      showOverflowTooltip: true,
      prop: "namespace"
    },
    {
      label: transformI18n("resource.column.deployment"),
      showOverflowTooltip: true,
      prop: "deployment"
    },
    {
      label: transformI18n("resource.column.podCount"),
      prop: "pod_count",
      sortable: true
    },
    {
      label: transformI18n("resource.column.p95PodQps"),
      prop: "p95_pod_qps",
      sortable: true,
      hide: true,
      formatter: ({ p95_pod_qps }) => p95_pod_qps.toFixed(2)
    },
    {
      label: transformI18n("resource.column.p95PodCpuPct"),
      prop: "p95_pod_cpu_pct",
      sortable: true,
      formatter: ({ p95_pod_cpu_pct }) => p95_pod_cpu_pct.toFixed(2) + "%"
    },
    {
      label: transformI18n("resource.column.p95PodLoad"),
      prop: "p95_pod_load",
      sortable: true,
      formatter: ({ p95_pod_load }) => p95_pod_load.toFixed(2)
    },
    {
      label: transformI18n("resource.column.requestPodCpuM"),
      prop: "request_pod_cpu_m",
      sortable: true,
      formatter: ({ request_pod_cpu_m }) => request_pod_cpu_m.toFixed(2)
    },
    {
      label: transformI18n("resource.column.limitPodCpuM"),
      prop: "limit_pod_cpu_m",
      sortable: true,
      formatter: ({ limit_pod_cpu_m }) => limit_pod_cpu_m.toFixed(2)
    },
    {
      label: transformI18n("resource.column.p95PodWssPct"),
      prop: "p95_pod_wss_pct",
      sortable: true,
      formatter: ({ p95_pod_wss_pct }) => p95_pod_wss_pct.toFixed(2) + "%"
    },
    {
      label: transformI18n("resource.column.p95PodWssMb"),
      prop: "p95_pod_wss_mb",
      sortable: true
    },
    {
      label: transformI18n("resource.column.requestPodMemMb"),
      prop: "request_pod_mem_mb",
      sortable: true,
      formatter: ({ request_pod_mem_mb }) => request_pod_mem_mb.toFixed(2)
    },
    {
      label: transformI18n("resource.column.limitPodMemMb"),
      prop: "limit_pod_mem_mb",
      sortable: true,
      formatter: ({ limit_pod_mem_mb }) => limit_pod_mem_mb.toFixed(2)
    },
    {
      label: transformI18n("resource.column.p95PodG1gcQps"),
      prop: "p95_pod_g1gc_qps",
      sortable: true,
      hide: true,
      formatter: ({ p95_pod_g1gc_qps }) => p95_pod_g1gc_qps.toFixed(2)
    },
    {
      label: transformI18n("resource.column.podJvmMaxMb"),
      prop: "pod_jvm_max_mb",
      sortable: true,
      formatter: ({ pod_jvm_max_mb }) => pod_jvm_max_mb.toFixed(2),
      hide: true
    },
    {
      label: transformI18n("resource.column.date"),
      prop: "date",
      hide: true
    }
  ];

  async function onSearch() {
    if (!queryForm.date || !queryForm.env) {
      message(transformI18n("resource.message.dateAndEnvIsNecessary"), {
        type: "warning"
      });
      return;
    }
    loading.value = true;
    const { data, meta } = await getCollection(queryForm.date, queryForm.env);
    dataList.value = data.map(item => {
      let obj = {};
      for (let index = 0; index < meta.length; index++) {
        const key = meta[index].name;
        obj[key] = item[index];
      }
      return obj;
    });
    loading.value = false;
  }

  function resetForm() {
    queryForm.date = "";
    queryForm.env = searchStore.env || "";
    onSearch();
  }

  // 监听 store 中的环境变化
  watch(
    () => searchStore.env,
    newVal => {
      if (newVal && newVal !== queryForm.env) {
        queryForm.env = newVal;
        onSearch();
      }
    }
  );

  onMounted(async () => {
    const [envRes] = await Promise.all([getEnv()]);
    envList.value = envRes.data;

    // 如果 store 中有环境值，触发搜索
    if (
      searchStore.env &&
      envList.value.includes(item => item[0] == searchStore.env)
    ) {
      queryForm.env = searchStore.env;
      onSearch();
    }
  });

  return {
    envList,
    queryForm,
    loading,
    columns,
    dataList,
    deviceDetection,
    onSearch,
    resetForm
  };
}
