<template>
  <div class="accordion" @click="toggle">
    <div
      class="accordion-header text-blueishBlack hover:bg-neutrals-100 flex cursor-pointer select-none items-center justify-between px-4 py-3 font-bold"
    >
      <div class="flex items-center gap-4">
        <slot name="icon" />
        <slot name="title" />
      </div>

      <Icon :name="icon" class="text-gray-500" />
    </div>
    <div
      v-show="isOpen"
      class="divide-neutrals-10 divide-y transition duration-300 ease-in-out"
    >
      <slot name="content" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import Icon from "../Icon.vue";

const isOpen = defineModel<boolean>({
  default: false,
});

function toggle() {
  isOpen.value = !isOpen.value;
}

const icon = computed(() => {
  return isOpen.value ? "IconChevronUp" : "IconChevronDown";
});
</script>
