const { VITE_HIDE_HOME } = import.meta.env;
// const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/monitnode",
  redirect: "/monitnode/index",
  meta: {
    icon: "ep:data-analysis",
    title: $t("menus.resourceMonitnode"),
    rank: 1
  },
  children: [
    {
      path: "/monitnode/index",
      name: "Monitnode",
      component: () => import("@/views/monitnode/index.vue"),
      meta: {
        title: $t("menus.resourceMonitnode"),
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    }
  ]
} satisfies RouteConfigsTable;
