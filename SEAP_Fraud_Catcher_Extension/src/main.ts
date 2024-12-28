// plugins
import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

// toast
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

// tooltip, dropdowns, etc
import FloatingVue from "floating-vue";
import "floating-vue/dist/style.css";

// main scss
import "@/assets/css/style.scss";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(Toast, {
  timeout: 1500,
  closeOnClick: true,
  pauseOnFocusLoss: false,
  pauseOnHover: true,
  draggable: true,
  showCloseButtonOnHover: false,
  hideProgressBar: true,
  closeButton: "button",
  icon: true,
  rtl: false,
  maxToasts: 3,
  shareAppContext: true,
});
app.use(FloatingVue);

app.mount("#app");
