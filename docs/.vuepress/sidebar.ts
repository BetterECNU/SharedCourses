import { sidebar } from "vuepress-theme-hope";

export default sidebar({
  "/": [
    "",
    {
      text: "华东师范大学课程共享计划",
      icon: "book",
      prefix: "courses/",
      link: "courses/",
      children: "structure",
    },
  ],
});
