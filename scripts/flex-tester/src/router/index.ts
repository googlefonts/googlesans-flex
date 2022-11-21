import Vue from "vue";
import VueRouter from "vue-router";
import SpacingOverlayView from "../views/SpacingOverlayView.vue";

Vue.use(VueRouter);

const router = new VueRouter({
  mode: "hash",
  base: import.meta.env.BASE_URL,
  routes: [
    { path: "/", redirect: "/spacing-overlay" },
    {
      path: "/spacing-overlay",
      name: "home",
      component: SpacingOverlayView,
    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue')
    // }
  ],
});

export default router;
