const { VITE_HIDE_HOME } = import.meta.env;
// const Layout = () => import("@/layout/index.vue");
import { $t } from "@/plugins/i18n";

export default {
  path: "/collection",
  redirect: "/collection/index",
  meta: {
    icon: "ep:calendar",
    title: $t("menus.resourceCollection"),
    rank: 4
  },
  children: [
    {
      path: "/collection/index",
      name: "collection",
      component: () => import("@/views/collection/index.vue"),
      meta: {
        title: $t("menus.resourceCollection"),
        showLink: VITE_HIDE_HOME === "true" ? false : true
      }
    }
  ]
} satisfies RouteConfigsTable;
