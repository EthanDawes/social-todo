import type { Post } from "./types";
import { postsManager } from "./store.svelte";

export function makeIntersectionObserver(postElement: HTMLElement, post: Post) {
  let hasBeenVisible = false;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        hasBeenVisible = true;
      } else if (hasBeenVisible) {
        postsManager.markRead(post.id);
      }
    });
  });

  if (postElement) {
    observer.observe(postElement);
  }

  return () => {
    if (postElement) {
      observer.unobserve(postElement);
    }
  };
}
