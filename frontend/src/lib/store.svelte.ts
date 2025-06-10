import type { PostsData } from "./types";
import { page } from "$app/state";
import { base } from "$app/paths";

class Posts {
  allPosts: PostsData = $state(
    localStorage.getItem("posts")
      ? JSON.parse(localStorage.getItem("posts")!)
      : {},
  );

  private readonly platform = $derived(page.url.pathname.substring(1));
  readonly platformPosts = $derived(
    Object.values(this.allPosts).filter(
      (post) => post.platform === this.platform,
    ),
  );

  constructor() {
    // Fetch and merge new posts
    fetch(base + "/posts")
      .then((res) => res.json())
      .then((newPosts: PostsData) => {
        this.allPosts = { ...newPosts, ...this.allPosts };
        this.savePosts();
      });
  }

  savePosts() {
    localStorage.setItem("posts", JSON.stringify(this.allPosts));
  }
}

export const postsManager = new Posts();
