import { defineUserConfig } from "vuepress";

import theme from "./theme.js";

export default defineUserConfig({
  base: "/",

  lang: "zh-CN",
  title: "SharedCourses",
  description: "Sharing Courses with ECNUers",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
});
