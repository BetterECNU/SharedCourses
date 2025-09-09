import { sidebar } from "vuepress-theme-hope";

export default sidebar({
  "/": [
    "",
    {
      text: "课程",
      icon: "book",
      prefix: "courses/",
      link: "courses/",
      children: "structure",
    },
  ],
});
