import type { PostsData } from "./types";
import { page } from "$app/state";
import { base } from "$app/paths";

const platform = $derived(page.url.pathname.substring(1));

class Posts {
  allPosts: PostsData = $state(
    localStorage.getItem("posts")
      ? JSON.parse(localStorage.getItem("posts")!)
      : {},
  );

  readonly platformPosts = $derived(
    Object.values(this.allPosts).filter(
      (post) => post.platform === platform && !post.viewed,
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

  markRead(id: string) {
    this.allPosts[id].viewed = new Date().toISOString();
    this.savePosts();
  }
}

export const postsManager = new Posts();
