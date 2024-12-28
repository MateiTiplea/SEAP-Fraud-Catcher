<template>
  <div>
    <DefineTemplate>
      <div
        class="hover:bg-neutrals-100 flex items-center gap-4 px-4 py-3"
        :class="{
          'bg-neutrals-100': isSelected,
          'pl-8': isChild,
        }"
      >
        <Icon
          v-if="icon"
          :name="icon"
          class="text-lg"
          :class="{
            'text-primary': isSelected,
            'text-neutrals-80': !isSelected,
          }"
        />
        <span
          class="text-md truncate font-medium"
          :class="{
            'text-primary': isSelected,
            'text-neutrals-80': !isSelected,
          }"
        >
          {{ name }}
        </span>
      </div>
    </DefineTemplate>

    <template v-if="!children?.length">
      <template v-if="to">
        <RouterLink :to="to" @click.prevent="handleClick">
          <ReuseTemplate />
        </RouterLink>
      </template>
      <template v-else>
        <button class="w-full" type="button" @click.prevent="handleClick">
          <ReuseTemplate />
        </button>
      </template>
    </template>

    <template v-else>
      <AccordionBase v-model="isAccordionOpen">
        <template #icon>
          <Icon
            v-if="icon"
            :name="icon"
            class="text-lg"
            :class="{
              'text-primary': isSelected,
              'text-neutrals-80': !isSelected,
            }"
          />
        </template>
        <template #title>
          <h6
            class="text-md font-medium"
            :class="{
              'text-primary': isSelected,
              'text-neutrals-80': !isSelected,
            }"
          >
            {{ name }}
          </h6>
        </template>

        <template v-if="$slots.children" #content>
          <slot name="children" />
        </template>
      </AccordionBase>
    </template>
  </div>
</template>

<script setup lang="ts">
import { createReusableTemplate } from "@vueuse/core";
import { reactive, toRef, toRefs, watchEffect } from "vue";
import Icon from "../Icon.vue";
import AccordionBase from "../accordion/AccordionBase.vue";

interface PopoverItemConfig {
  id?: number;
  name?: string;
  icon?: string;
  to?: string;
  isSelected?: boolean;
  action?: string;
  closeOnClick?: boolean;
  children?: PopoverItemConfig[];
  isChild?: boolean;
  isOpen?: boolean;
}

const props = withDefaults(
  defineProps<{ itemConfig?: Partial<PopoverItemConfig> }>(),
  {
    itemConfig: () => ({}),
  },
);

const state = reactive({
  ...{
    id: 0,
    name: "",
    icon: "",
    to: "",
    isSelected: false,
    action: "",
    closeOnClick: true,
    children: [],
    isChild: false,
    isOpen: false,
  },
  ...props.itemConfig,
});

// Ensure the state stays updated if props.itemConfig changes
watchEffect(() => {
  Object.assign(state, props.itemConfig);
});

const {
  name,
  icon,
  to,
  isSelected,
  action,
  closeOnClick,
  children,
  isChild,
  isOpen,
  id,
} = toRefs(state);

const emit = defineEmits<{
  action: [
    {
      action: string;
      name?: string;
      id?: number;
    },
  ];
  click: [];
}>();

const [DefineTemplate, ReuseTemplate] = createReusableTemplate();

const isAccordionOpen = toRef(isOpen.value);

const handleClick = () => {
  if (action?.value) {
    emit("action", {
      action: action.value,
      name: name.value,
      id: id.value,
    });
  }
  if (closeOnClick?.value) {
    emit("click");
  }
};
</script>
