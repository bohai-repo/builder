const { VITE_HIDE_HOME } = import.meta.env;
// const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/workbench",
  redirect: "/workbench/index",
  meta: {
    icon: "ep:setting",
    title: $t("menus.resourceWorkbench"),
    rank: 5
  },
  children: [
    {
      path: "/workbench/index",
      name: "workbench",
      component: () => import("@/views/workbench/index.vue"),
      meta: {
        title: $t("menus.resourceWorkbench"),
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    }
  ]
} satisfies RouteConfigsTable;
