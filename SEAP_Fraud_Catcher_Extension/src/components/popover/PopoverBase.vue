<template>
  <Popover v-slot="{ open }" class="relative">
    <PopoverButton
      class="group inline-flex items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75"
    >
      <slot name="trigger" :open />
    </PopoverButton>

    <transition
      enter-active-class="transition ease-out duration-100 transform"
      enter-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75 transform"
      leave-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <PopoverPanel
        v-slot="{ close }"
        class="ring-blueishBlack absolute right-0 z-30 mt-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-opacity-5 focus:outline-none"
      >
        <div class="divide-neutrals-10 divide-y">
          <slot name="items" :close />
        </div>
      </PopoverPanel>
    </transition>
  </Popover>
</template>

<script setup lang="ts">
import { Popover, PopoverButton, PopoverPanel } from "@headlessui/vue";

defineSlots<{
  trigger?: (props: { open: boolean }) => any;
  items?: (props: { close: () => void }) => any;
}>();
</script>
