import { defineUserConfig } from "vuepress";

import theme from "./theme.js";

export default defineUserConfig({
  base: "/",

  lang: "zh-CN",
  title: "ECNU·课栈",
  description: "华东师范大学课程共享计划 - 统一汇总，公开共享，开放更新\nECNU SharedCourses - Sharing Courses with ECNUers",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
});
