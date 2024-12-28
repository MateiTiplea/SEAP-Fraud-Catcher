<template>
  <div class="relative flex h-screen min-h-[600px] max-w-[500px]">
    <div class="relative flex h-full w-full flex-col">
      <Header />
      <main class="flex-1">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from "@/components/Header.vue";
</script>
