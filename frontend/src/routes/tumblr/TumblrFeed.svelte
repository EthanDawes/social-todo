<script lang="ts">
    import { postsManager } from "$lib/store.svelte";
    import TumblrPost from "./TumblrPost.svelte";

    let posts = $derived(postsManager.platformPosts);
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
        {#each posts as post (post.id)}
            <TumblrPost {post} />
        {/each}

        {#if posts.length === 0}
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

    .tumblr-sidebar {
        background-color: var(--tumblr-blue);
    }

    .tumblr-feed {
        font-family: "Helvetica Neue", Arial, sans-serif;
        padding: 1rem;
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
    }

    @media (max-width: 640px) {
        .tumblr-feed {
            padding: 0.25rem;
        }
    }
</style>
