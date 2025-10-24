def get_top_k_posts_by_score(posts: dict, k: int) -> dict:
    top_post_ids = sorted(posts.keys(), key=lambda pid: posts[pid]["metadata"]["score"], reverse=True)[:k]
    return {pid: posts[pid] for pid in top_post_ids}
