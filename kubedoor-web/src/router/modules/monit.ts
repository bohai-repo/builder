const { VITE_HIDE_HOME } = import.meta.env;
const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/",
  redirect: "/monit/index",
  component: Layout,
  meta: {
    icon: "ep:monitor",
    title: $t("menus.resourceMonit"),
    rank: 1
  },
  children: [
    {
      path: "/monit/index",
      name: "Monit",
      component: () => import("@/views/monit/index.vue"),
      meta: {
        title: $t("menus.RealtimeResource"),
        icon: "ep:data-analysis",
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    },
    {
      path: "/monitk8s/index",
      name: "Monitk8s",
      component: () => import("@/views/monitk8s/index.vue"),
      meta: {
        title: $t("menus.resourceMonitk8s"),
        icon: "ep:odometer",
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    },
    {
      path: "/monitnode/index",
      name: "Monitnode",
      component: () => import("@/views/monitnode/index.vue"),
      meta: {
        title: $t("menus.resourceMonitnode"),
        icon: "ep:data-analysis",
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    }
  ]
} satisfies RouteConfigsTable;
