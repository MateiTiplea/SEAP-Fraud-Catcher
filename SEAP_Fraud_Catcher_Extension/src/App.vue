<template>
  <div class="h-[600px] w-[500px]" :key="refreshLayout">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { useLayoutStore } from "./stores/layout.store";
import { storeToRefs } from "pinia";
const layoutStore = useLayoutStore();
const { refreshLayout } = storeToRefs(layoutStore);
</script>
