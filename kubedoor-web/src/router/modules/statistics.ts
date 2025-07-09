const { VITE_HIDE_HOME } = import.meta.env;
// const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/statistics",
  redirect: "/statistics/index",
  meta: {
    icon: "ep:pie-chart",
    title: $t("menus.resourceStatistics"),
    rank: 3
  },
  children: [
    {
      path: "/statistics/index",
      name: "Statistics",
      component: () => import("@/views/statistics/index.vue"),
      meta: {
        title: $t("menus.resourceStatistics"),
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    }
  ]
} satisfies RouteConfigsTable;
