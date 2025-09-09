import { navbar } from "vuepress-theme-hope";

export default navbar([
  "/",
  {
    text: "课程",
    icon: "book",
    link: "/courses/",
    activeMatch: "^/courses/",
  },
]);
