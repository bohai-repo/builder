// const { VITE_HIDE_HOME } = import.meta.env;
// const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/alarm",
  redirect: "/alarm/statistics",
  meta: {
    icon: "ep:bell",
    title: $t("menus.alarm"),
    rank: 0
  },
  children: [
    {
      path: "/alarm/statistics",
      name: "alarm-statistics",
      component: () => import("@/views/alarm/index.vue"),
      meta: {
        title: $t("menus.alarmStatistics"),
        icon: "ep:data-line"
      }
    },
    {
      path: "/alarm/detail",
      name: "alarm-detail",
      component: () => import("@/views/alarm/detail.vue"),
      meta: {
        title: $t("menus.alarmDetail"),
        icon: "ep:list"
      }
    }
  ]
} satisfies RouteConfigsTable;
