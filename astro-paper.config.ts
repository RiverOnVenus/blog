import { defineAstroPaperConfig } from "./src/types/config";

export default defineAstroPaperConfig({
  site: {
    url: "https://zhui.dev",
    title: "Error: 你发现了一个错误！",
    description: "Life often requires some excitement, joy, and anticipation.",
    author: "Mr. Error 追",
    profile: "https://github.com/RiverOnVenus",
    ogImage: "default-og.jpg",
    lang: "zh-CN",
    timezone: "Asia/Shanghai",
    dir: "ltr",
  },
  posts: {
    perPage: 5,
    perIndex: 5,
    scheduledPostMargin: 15 * 60 * 1000,
  },
  features: {
    lightAndDarkMode: true,
    dynamicOgImage: true,
    showArchives: true,
    showBackButton: true,
    editPost: {
      enabled: false,
    },
    search: "pagefind",
  },
  socials: [
    { name: "github", url: "https://github.com/RiverOnVenus" },
    { name: "x", url: "https://x.com/RiverOnVenus" },
    { name: "telegram", url: "https://t.me/RiverOnVenus" },
    { name: "mail", url: "mailto:error@zhui.dev" },
  ],
  shareLinks: [
    { name: "x", url: "https://x.com/intent/post?url=" },
    { name: "telegram", url: "https://t.me/share/url?url=" },
    { name: "mail", url: "mailto:?subject=See%20this%20post&body=" },
  ],
});
