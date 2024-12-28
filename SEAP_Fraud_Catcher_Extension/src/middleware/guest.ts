//import { useAuthStore } from "@/stores/auth.store";
import { storeToRefs } from "pinia";
import type { NavigationGuardNext } from "vue-router";

/**
 * Middleware to check if the user is only a guest
 */
export default function guest({ next }: { next: NavigationGuardNext }) {
  //const { isLoggedIn } = storeToRefs(useAuthStore());
  /*
  if (isLoggedIn.value) {
    return next({
      name: "home",
    });
  }
*/
  return next();
}
