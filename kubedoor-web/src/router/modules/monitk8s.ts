const { VITE_HIDE_HOME } = import.meta.env;
// const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/monitk8s",
  redirect: "/monitk8s/index",
  meta: {
    icon: "ep:odometer",
    title: $t("menus.resourceMonitk8s"),
    rank: 2
  },
  children: [
    {
      path: "/monitk8s/index",
      name: "Monitk8s",
      component: () => import("@/views/monitk8s/index.vue"),
      meta: {
        title: $t("menus.resourceMonitk8s"),
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    }
  ]
} satisfies RouteConfigsTable;
