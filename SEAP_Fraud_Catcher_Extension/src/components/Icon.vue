<template>
  <component
    :is="iconComponent"
    v-if="iconComponent"
    :width="size"
    :height="size"
  />
  <span v-else>Icon not found</span>
</template>

<script setup lang="ts">
import { shallowRef, watchEffect, type Component } from "vue";

const icons = import.meta.glob("./icons/*.vue") as Record<
  string,
  () => Promise<{ default: Component }>
>;

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  size: {
    type: [String, Number],
    default: 22,
  },
});

const iconComponent = shallowRef();

const loadIcon = async () => {
  const iconPath = `./icons/${props.name}.vue`;
  if (icons[iconPath]) {
    iconComponent.value = (await icons[iconPath]()).default;
  }
};

watchEffect(() => {
  loadIcon();
});
</script>
