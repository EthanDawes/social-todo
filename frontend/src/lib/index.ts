import type { PostsData } from "./types";
import { page } from '$app/state';
import { base } from '$app/paths';

export let allPosts: PostsData = $state(
  localStorage.getItem("posts")
    ? JSON.parse(localStorage.getItem("posts")!)
    : {}
);

export const savePosts = () => localStorage.setItem("posts", JSON.stringify(allPosts));

const platform = $derived(page.url.pathname.substring(1));
export const platformPosts = $derived(Object.values(allPosts).filter(
  (post) => post.platform === platform,
));

// Fetch and merge new posts
const newPosts: PostsData = await (await fetch(base + "/posts")).json();
allPosts = {...newPosts, ...allPosts}
savePosts();
