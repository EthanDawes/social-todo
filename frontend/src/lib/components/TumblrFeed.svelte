<script lang="ts">
  import { marked } from 'marked';
  import type { TumblrPostsData } from '$lib/types/tumblr.ts';

  interface Props {
    posts: TumblrPostsData;
  }

  const { posts }: Props = $props();

  // Convert posts object to array and sort by most recent (using id as proxy)
  const postsArray = $derived(
    Object.values(posts).sort((a, b) => b.id.localeCompare(a.id))
  );

  function renderMarkdown(content: string): string {
    return marked(content, { 
      breaks: true,
      gfm: true 
    });
  }

  function formatModel(model: string): string {
    return model.replace('gpt-', 'GPT-').replace('-', ' ');
  }

  function truncateOverview(overview: string, maxLength: number = 80): string {
    return overview.length > maxLength 
      ? overview.substring(0, maxLength) + '...' 
      : overview;
  }
</script>

<div class="tumblr-feed max-w-2xl mx-auto p-4 space-y-6">
  <!-- Feed Header -->
  <div class="text-center py-6">
    <h1 class="text-3xl font-bold text-blue-600 mb-2">Tumblr Feed</h1>
    <p class="text-gray-600">Generated posts from your todo list</p>
  </div>

  <!-- Posts -->
  {#each postsArray as post (post.id)}
    <article class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-200">
      <!-- Post Header -->
      <div class="border-b border-gray-100 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span class="text-white font-bold text-sm">AI</span>
            </div>
            <div>
              <h3 class="font-semibold text-gray-800">AI Assistant</h3>
              <p class="text-sm text-gray-500">{formatModel(post.model)}</p>
            </div>
          </div>
          <div class="text-xs text-gray-400">
            #{post.id.substring(0, 8)}
          </div>
        </div>
      </div>

      <!-- Post Overview -->
      <div class="px-4 py-3 bg-gray-50 border-b border-gray-100">
        <p class="text-sm font-medium text-gray-700">
          📝 {truncateOverview(post.overview)}
        </p>
      </div>

      <!-- Post Content -->
      <div class="p-4">
        <div class="prose prose-sm max-w-none">
          {@html renderMarkdown(post.post)}
        </div>
      </div>

      <!-- Post Footer -->
      <div class="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center space-x-4">
            <button class="flex items-center space-x-1 text-gray-500 hover:text-red-500 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span>Like</span>
            </button>
            <button class="flex items-center space-x-1 text-gray-500 hover:text-blue-500 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span>Reblog</span>
            </button>
            <button class="flex items-center space-x-1 text-gray-500 hover:text-green-500 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
              <span>Share</span>
            </button>
          </div>
          <div class="text-gray-400">
            <span class="inline-block w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
            {post.platform}
          </div>
        </div>
      </div>
    </article>
  {/each}

  {#if postsArray.length === 0}
    <div class="text-center py-12">
      <div class="text-gray-400 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-600 mb-2">No posts yet</h3>
      <p class="text-gray-500">Your Tumblr feed will appear here once you have posts.</p>
    </div>
  {/if}
</div>

<style>
  .tumblr-feed :global(.prose) {
    color: #374151;
  }
  
  .tumblr-feed :global(.prose h1),
  .tumblr-feed :global(.prose h2),
  .tumblr-feed :global(.prose h3),
  .tumblr-feed :global(.prose h4),
  .tumblr-feed :global(.prose h5),
  .tumblr-feed :global(.prose h6) {
    color: #1f2937;
    font-weight: 600;
  }
  
  .tumblr-feed :global(.prose a) {
    color: #3b82f6;
    text-decoration: none;
  }
  
  .tumblr-feed :global(.prose a:hover) {
    text-decoration: underline;
  }
  
  .tumblr-feed :global(.prose code) {
    background-color: #f3f4f6;
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
  }
  
  .tumblr-feed :global(.prose blockquote) {
    border-left: 4px solid #e5e7eb;
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
    color: #6b7280;
  }
  
  .tumblr-feed :global(.prose ul),
  .tumblr-feed :global(.prose ol) {
    padding-left: 1.5rem;
  }
  
  .tumblr-feed :global(.prose li) {
    margin: 0.25rem 0;
  }
</style>