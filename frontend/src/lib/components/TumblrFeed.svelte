<script lang="ts">
    import { marked } from "marked";
    import type { TumblrPostsData } from "$lib/types/tumblr.ts";

    interface Props {
        posts: TumblrPostsData;
    }

    const { posts }: Props = $props();

    // Convert posts object to array and sort by most recent (using id as proxy)
    const postsArray = $derived(
        Object.values(posts).sort((a, b) => b.id.localeCompare(a.id)),
    );

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
</script>

<div class="tumblr-container bg-tumblr-blue min-h-screen">
    <!-- Sidebar -->
    <div
        class="tumblr-sidebar fixed left-0 top-0 w-80 h-full bg-tumblr-blue p-6 overflow-y-auto md:block hidden"
    >
        <!-- Tumblr Logo -->
        <div class="mb-8">
            <h1 class="text-black text-4xl font-bold tracking-tight">tumblr</h1>
        </div>

        <!-- Navigation -->
        <nav class="space-y-4 mb-8">
            <a
                href="#"
                class="flex items-center space-x-3 text-black hover:text-blue-200 transition-colors py-2"
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
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                </svg>
                <span class="text-lg">Explore</span>
            </a>

            <a
                href="#"
                class="flex items-center space-x-3 text-black hover:text-blue-200 transition-colors py-2"
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
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                </svg>
                <span class="text-lg">Communities</span>
            </a>

            <a
                href="#"
                class="flex items-center space-x-3 text-black hover:text-blue-200 transition-colors py-2"
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
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                </svg>
                <span class="text-lg">Canary</span>
                <span class="text-sm text-gray-400">(6/12)</span>
            </a>
        </nav>

        <!-- Action Buttons -->
        <div class="space-y-3">
            <button
                class="w-full bg-orange-500 hover:bg-orange-600 text-black font-bold py-3 px-6 rounded-full transition-colors"
            >
                Sign up
            </button>
            <button
                class="w-full border border-white text-black hover:bg-white hover:text-tumblr-blue font-bold py-3 px-6 rounded-full transition-colors"
            >
                Log in
            </button>
        </div>
    </div>

    <!-- Main Content -->
    <div class="tumblr-feed md:ml-80 ml-0 max-w-xl mx-auto min-h-screen">
        <!-- Posts -->
        {#each postsArray as post (post.id)}
            <article
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
                            <h3 class="font-bold text-lg text-black mr-2">
                                ai-assistant
                            </h3>
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
                        <svg
                            class="w-5 h-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                        >
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
        {/each}

        {#if postsArray.length === 0}
            <div class="text-center py-12 px-4">
                <div class="text-gray-400 mb-4">
                    <svg
                        class="w-16 h-16 mx-auto"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        />
                    </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-600 mb-2">
                    No posts yet
                </h3>
                <p class="text-gray-500">
                    Your Tumblr feed will appear here once you have posts.
                </p>
            </div>
        {/if}
    </div>
</div>

<style>
    .tumblr-container {
        font-family: "Helvetica Neue", Arial, sans-serif;
        --tumblr-blue: #ffffe8;
    }

    .bg-tumblr-blue {
        background-color: var(--tumblr-blue);
    }

    .text-tumblr-blue {
        color: var(--tumblr-blue);
    }

    .tumblr-sidebar {
        background-color: var(--tumblr-blue);
    }

    .tumblr-feed {
        font-family: "Helvetica Neue", Arial, sans-serif;
        padding: 1rem;
    }

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
        .tumblr-sidebar {
            display: none;
        }

        .tumblr-feed {
            margin-left: 0;
            padding: 0.5rem;
        }

        .tumblr-post {
            margin-bottom: 1rem;
        }
    }

    @media (max-width: 640px) {
        .tumblr-feed {
            padding: 0.25rem;
        }

        .tumblr-post {
            border-radius: 0.5rem;
        }
    }
</style>
