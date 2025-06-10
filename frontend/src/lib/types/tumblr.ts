export interface TumblrPost {
  id: string;
  platform: "tumblr" | "twitter" | "4chan";
  model: string;
  prompt: string;
  overview: string;
  post: string;
}

export interface TumblrPostsData {
  [key: string]: TumblrPost;
}

export interface TumblrFeedProps {
  posts: TumblrPostsData;
}
