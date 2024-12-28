<template>
  <button
    type="button"
    :class="getClasses"
    :disabled="disabled"
    @click.prevent="emitClick($event)"
  >
    <slot v-if="!loading || disabled" />
    <IconLoader v-else />
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";
import IconLoader from "./icons/IconLoader.vue";

interface ButtonProps {
  disabled?: boolean;
  loading?: boolean;
  variant?:
    | "primary"
    | "secondary"
    | "tertiary"
    | "flat"
    | "round"
    | "round-primary";
  size?: "compact" | "default" | "none";
  fullwidth?: boolean;
}

defineSlots<{
  default?: () => any;
}>();

const props = withDefaults(defineProps<ButtonProps>(), {
  disabled: false,
  loading: false,
  variant: "primary",
  size: "default",
  fullwidth: false,
});

/**
 * Compute Classes based on passed props
 */
const getClasses = computed(() => {
  const baseClasses =
    "flex items-center justify-center whitespace-nowrap rounded-lg px-2.5 text-center text-base font-semibold";

  const loadingClasses = "cursor-pointer-events-none";

  const disabledClasses = {
    primary:
      "cursor-pointer-events-none text-gray-500 bg-[#1AC2FF]  cursor-not-allowed",
    secondary:
      "cursor-pointer-events-none text-gray-500 bg-[#1AC2FF]  cursor-not-allowed",
    tertiary:
      "hover:bg-[#1AC2FF] cursor-pointer-events-none cursor-not-allowed",
    flat: "cursor-pointer-events-none text-gray-500 bg-[#1AC2FF]  cursor-not-allowed",
    round:
      "cursor-pointer-events-none text-gray-500 bg-[#1AC2FF]  cursor-not-allowed",
    "round-primary":
      "cursor-pointer-events-none text-gray-500 bg-[#1AC2FF]  cursor-not-allowed",
  };

  const colorClasses = {
    primary: "bg-[#1AC2FF] hover:bg-opacity-90 text-white px-2.5 rounded-lg",
    secondary:
      "bg-transparent text-neutrals-90 hover:bg-neutrals-20 border border-neutrals-20 px-2.5 rounded-lg ",
    tertiary:
      "bg-transparent text-neutrals-90 hover:bg-neutrals-70 px-2.5 rounded-lg ",
    flat: "bg-transparent text-neutrals-90 px-2.5 rounded-lg ",
    round: "bg-zinc-50 text-primary rounded-full",
    "round-primary": "bg-primary text-white rounded-full",
  };

  const sizeClasses = {
    default: "min-h-[20px] py-1 sm:min-h-[40px] sm:py-2",
    compact: "min-h-[20px] py-1",
    none: "",
  };

  const fullWidthClasses = props.fullwidth ? "w-full" : "";

  return [
    baseClasses,
    loadingClasses,
    sizeClasses[props.size],
    fullWidthClasses,
    props.disabled
      ? disabledClasses[props.variant]
      : colorClasses[props.variant],
    props.loading ? loadingClasses : "",
  ]
    .join(" ")
    .trim();
});

const emit = defineEmits(["click"]);

/**
 * Emit a click only if the button is not disabled or loading
 */
const emitClick = (event: Event) => {
  if (!props.disabled && !props.loading) {
    emit("click", event);
  }
};
</script>
