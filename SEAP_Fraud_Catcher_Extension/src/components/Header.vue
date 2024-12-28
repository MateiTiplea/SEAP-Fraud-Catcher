<template>
  <div
    class="relative z-10 ml-[-60px] flex h-16 items-center justify-between border-b px-6 py-3"
  >
    <Logo />
    <div
      class="relative ml-[-60px] font-mono text-2xl font-bold text-[#1AC2FF]"
    >
      SEAP Fraud Catcher
      <span
        class="absolute bottom-0 left-0 h-[0.5px] w-full bg-[#1AC2FF]"
      ></span>
    </div>

    <div class="relative flex items-center justify-center">
      <PopoverBase>
        <template #trigger>
          <ProfileAvatar />
        </template>
        <template #items="{ close }">
          <PopoverItem
            v-for="(item, index) in menuItems"
            :key="index"
            :item-config="item"
            @action="handleAction"
            @click="close"
          >
          </PopoverItem>
        </template>
      </PopoverBase>
    </div>
  </div>
</template>

<script setup lang="ts">
import Logo from "./icons/Logo.vue";
import { useToast } from "vue-toastification";
import PopoverBase from "./popover/PopoverBase.vue";
import PopoverItem from "./popover/PopoverItem.vue";
import { useRouter } from "vue-router";
import { computed } from "vue";
import ProfileAvatar from "./ProfileAvatar.vue";

const toast = useToast();

const menuItems = computed(() => [
  { name: "Log Out", icon: "IconLogout", action: "logout" },
]);

const router = useRouter();

const handleAction = async ({
  action,
  id,
}: {
  action: string;
  id?: number;
  name?: string;
}) => {
  if (action === "logout") {
    //await authStore.logout();
    toast.success("Logout succesful!");
    await router.push("/login");
  }
};
</script>
