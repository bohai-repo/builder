import { defineStore } from "pinia";
import { store } from "../utils";
import { storageLocal } from "../utils";

interface SearchConfig {
  env: string;
  namespace: string;
}

const searchKey = "search-config";

export const useSearchStore = defineStore({
  id: "pure-search",
  state: (): SearchConfig => ({
    // 环境
    env: storageLocal().getItem<SearchConfig>(searchKey)?.env ?? "",
    // 命名空间
    namespace: storageLocal().getItem<SearchConfig>(searchKey)?.namespace ?? ""
  }),

  getters: {
    // 获取完整的搜索参数
    getSearchParams: state => {
      return {
        env: state.env,
        namespace: state.namespace
      };
    }
  },

  actions: {
    // 设置环境
    setEnv(env: string) {
      this.env = env;
      this.saveToStorage();
    },

    // 设置命名空间
    setNamespace(namespace: string) {
      this.namespace = namespace;
      this.saveToStorage();
    },

    // 保存到 localStorage
    saveToStorage() {
      storageLocal().setItem(searchKey, {
        env: this.env,
        namespace: this.namespace
      });
    },

    // 清除存储
    clearStorage() {
      storageLocal().removeItem(searchKey);
      this.env = "";
      this.namespace = "";
    }
  }
});

export function useSearchStoreHook() {
  return useSearchStore(store);
}
