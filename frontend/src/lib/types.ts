export interface Post {
  id: string;
  platform: "tumblr" | "twitter" | "4chan";
  model: string;
  prompt: string;
  overview: string;
  post: string;
}

// Map id to Post
export type PostsData = Record<string, Post>;

export interface FeedProps {
  posts: PostsData;
}
