import { defineStore } from "pinia";

export const useLayoutStore = defineStore({
  id: "layoutStore",

  state: () => ({
    selectTab: 0,
    refreshLayout: 0,
    layoutLoading: false,
  }),

  actions: {},

  getters: {},
});
