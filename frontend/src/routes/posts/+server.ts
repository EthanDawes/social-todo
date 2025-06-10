import { json } from "@sveltejs/kit";

export async function GET() {
  // Load posts.json and serve
  const posts = await import("@/../../../backend/posts.json");
  return json(posts);
}
