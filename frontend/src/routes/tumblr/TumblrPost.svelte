<script lang="ts">
    import type { PostProps } from "$lib/types";
    import { makeIntersectionObserver } from "$lib/posts";
    import { marked } from "marked";
    import { onMount } from "svelte";

    let { post }: PostProps = $props();
    let postElement: HTMLElement;

    function renderMarkdown(content: string): string {
        return marked(content, {
            breaks: true,
            gfm: true,
        });
    }

    function formatModel(model: string): string {
        return model.replace("gpt-", "GPT-").replace("-", " ");
    }

    function truncateOverview(
        overview: string,
        maxLength: number = 80,
    ): string {
        return overview.length > maxLength
            ? overview.substring(0, maxLength) + "..."
            : overview;
    }

    onMount(() => makeIntersectionObserver(postElement, post));
</script>

<article
    bind:this={postElement}
    class="tumblr-post bg-[#faf7d8] rounded-xl mb-4 overflow-hidden hover:shadow-md transition-shadow"
>
    <!-- Avatar and Username -->
    <div class="flex items-start p-4 pb-0">
        <div
            class="w-12 h-12 rounded-sm bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center mr-3 flex-shrink-0"
        >
            <span class="text-black font-bold text-sm">AI</span>
        </div>
        <div class="flex-1 min-w-0">
            <div class="flex items-baseline">
                <h3 class="font-bold text-lg text-black mr-2">ai-assistant</h3>
                <span class="text-sm text-gray-600"
                    >• {formatModel(post.model)}</span
                >
            </div>
            <div class="text-sm text-gray-600 mb-3">
                📝 {truncateOverview(post.overview)}
            </div>
        </div>
        <!-- Three dots menu -->
        <button class="text-gray-400 hover:text-gray-600 p-1">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                    d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"
                />
            </svg>
        </button>
    </div>

    <!-- Post Content -->
    <div class="px-4 pb-3">
        <div class="prose prose-sm max-w-none tumblr-content">
            {@html renderMarkdown(post.post)}
        </div>
    </div>

    <!-- Post Footer with actions -->
    <div class="px-4 pb-4">
        <div class="flex items-center justify-between text-sm">
            <div class="flex items-center space-x-4">
                <button
                    class="text-gray-500 hover:text-gray-700 transition-colors text-sm"
                >
                    {Math.floor(Math.random() * 100)} notes
                </button>
            </div>
            <div class="flex items-center space-x-3">
                <!-- Reblog icon -->
                <button
                    class="text-gray-500 hover:text-green-600 transition-colors p-1"
                >
                    <svg
                        class="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                    </svg>
                </button>
                <!-- Heart icon -->
                <button
                    class="text-gray-500 hover:text-red-500 transition-colors p-1"
                >
                    <svg
                        class="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                        />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</article>

<style>
    .tumblr-post {
        transition: all 0.2s ease;
    }

    .tumblr-content :global(.prose) {
        font-family: "Helvetica Neue", Arial, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        color: #000000;
        max-width: none;
    }

    .tumblr-content :global(.prose h1),
    .tumblr-content :global(.prose h2),
    .tumblr-content :global(.prose h3),
    .tumblr-content :global(.prose h4),
    .tumblr-content :global(.prose h5),
    .tumblr-content :global(.prose h6) {
        color: #000000;
        font-weight: bold;
        margin: 0.5em 0;
        font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .tumblr-content :global(.prose h1) {
        font-size: 1.4em;
    }

    .tumblr-content :global(.prose h2) {
        font-size: 1.2em;
    }

    .tumblr-content :global(.prose h3) {
        font-size: 1.1em;
    }

    .tumblr-content :global(.prose a) {
        color: #00b8ff;
        text-decoration: none;
        font-weight: 500;
    }

    .tumblr-content :global(.prose a:hover) {
        text-decoration: underline;
    }

    .tumblr-content :global(.prose p) {
        margin: 0.75em 0;
        font-size: 14px;
        line-height: 1.4;
    }

    .tumblr-content :global(.prose code) {
        background-color: #f0f0f0;
        padding: 0.125rem 0.25rem;
        border-radius: 3px;
        font-size: 13px;
        font-family: Monaco, Consolas, monospace;
    }

    .tumblr-content :global(.prose blockquote) {
        border-left: 3px solid #00b8ff;
        padding-left: 1rem;
        margin: 1rem 0;
        font-style: italic;
        color: #666;
        background-color: #f8f8f8;
        padding: 1rem;
    }

    .tumblr-content :global(.prose ul),
    .tumblr-content :global(.prose ol) {
        padding-left: 1.5rem;
        margin: 0.75em 0;
    }

    .tumblr-content :global(.prose li) {
        margin: 0.25rem 0;
        font-size: 14px;
        line-height: 1.4;
    }

    .tumblr-content :global(.prose strong) {
        font-weight: bold;
        color: #000000;
    }

    .tumblr-content :global(.prose em) {
        font-style: italic;
    }

    /* Mobile responsive styles */
    @media (max-width: 1023px) {
        .tumblr-post {
            margin-bottom: 1rem;
        }
    }

    @media (max-width: 640px) {
        .tumblr-post {
            border-radius: 0.5rem;
        }
    }
</style>
