import { readFile } from "fs/promises";

export async function GET() {
  // Load posts.json and serve
  const data = await readFile("../backend/posts.json");

  return new Response(data, {
    headers: { "Content-Type": "application/json" },
  });
}
