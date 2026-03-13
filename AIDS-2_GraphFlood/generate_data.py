"""
Generate synthetic social network data for GraphFlood challenge
- Social graph (sampled from 10M users, 500M edges)
- Content stream
- Fact-check database
- Historical cascades
"""

import numpy as np
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

np.random.seed(42)
random.seed(42)

# Parameters (scaled down for practical generation)
NUM_USERS = 100000  # Sample of 10M users
AVG_FOLLOWERS = 50  # Average followers per user
NUM_POSTS = 50000
NUM_FACT_CHECKS = 10000
NUM_CASCADES = 5000

# User types
USER_TYPES = [
    {"type": "regular", "weight": 0.7, "post_freq": 1.0, "credibility": 0.8},
    {"type": "influencer", "weight": 0.1, "post_freq": 5.0, "credibility": 0.9},
    {"type": "news_org", "weight": 0.05, "post_freq": 10.0, "credibility": 0.95},
    {"type": "bot", "weight": 0.1, "post_freq": 20.0, "credibility": 0.2},
    {"type": "troll", "weight": 0.05, "post_freq": 15.0, "credibility": 0.1},
]

# Topic categories
TOPICS = [
    "politics", "health", "technology", "sports", "entertainment",
    "science", "business", "world_news", "environment", "education"
]

# Misinformation types
MISINFO_TYPES = [
    "false_claim", "misleading", "out_of_context", "satire", 
    "conspiracy", "manipulated_media", "fake_expert"
]


def generate_user(user_id: int) -> Dict:
    """Generate a user profile"""
    user_type = np.random.choice(
        [ut["type"] for ut in USER_TYPES],
        p=[ut["weight"] for ut in USER_TYPES]
    )
    
    type_info = next(ut for ut in USER_TYPES if ut["type"] == user_type)
    
    # Generate follower count based on user type
    if user_type == "influencer":
        followers = int(np.random.lognormal(10, 2))
    elif user_type == "news_org":
        followers = int(np.random.lognormal(12, 1.5))
    elif user_type == "bot":
        followers = int(np.random.lognormal(6, 3))
    else:
        followers = int(np.random.lognormal(4, 2))
    
    followers = min(followers, 10000000)  # Cap at 10M
    
    return {
        "user_id": f"U{user_id:08d}",
        "username": f"user_{user_id}",
        "user_type": user_type,
        "followers": followers,
        "following": int(followers * np.random.uniform(0.5, 2.0)),
        "posts_count": int(np.random.lognormal(5, 2)),
        "account_age_days": int(np.random.uniform(30, 3650)),
        "credibility_score": type_info["credibility"] + np.random.normal(0, 0.1),
        "is_verified": np.random.random() < (0.8 if user_type in ["influencer", "news_org"] else 0.05),
        "location": np.random.choice(["US", "UK", "EU", "Asia", "Other"]),
        "topics_of_interest": random.sample(TOPICS, k=random.randint(1, 5))
    }


def generate_social_graph(users: List[Dict]) -> List[Dict]:
    """Generate follower/following relationships"""
    edges = []
    user_ids = [u["user_id"] for u in users]
    
    print("  Generating social graph edges...")
    
    for i, user in enumerate(users):
        if i % 10000 == 0:
            print(f"    Processing user {i}/{len(users)}...")
        
        # Number of people this user follows
        num_following = min(user["following"], len(users) - 1)
        
        # Preferential attachment - popular users get more followers
        popularity_weights = np.array([u["followers"] + 1 for u in users])
        popularity_weights[i] = 0  # Can't follow self
        popularity_weights = popularity_weights / popularity_weights.sum()
        
        # Select who to follow
        following_indices = np.random.choice(
            len(users),
            size=min(num_following, 1000),  # Cap for performance
            p=popularity_weights,
            replace=False
        )
        
        for idx in following_indices:
            edges.append({
                "follower": user["user_id"],
                "following": users[idx]["user_id"],
                "timestamp": (datetime(2024, 1, 1) + timedelta(
                    days=random.randint(0, user["account_age_days"])
                )).isoformat()
            })
    
    return edges


def generate_post(post_id: int, users: List[Dict]) -> Dict:
    """Generate a social media post"""
    user = random.choice(users)
    
    # Determine if post contains misinformation
    is_misinformation = np.random.random() < 0.15  # 15% misinformation
    
    topic = random.choice(TOPICS)
    
    if is_misinformation:
        misinfo_type = random.choice(MISINFO_TYPES)
        credibility = np.random.beta(2, 5)  # Low credibility
    else:
        misinfo_type = None
        credibility = np.random.beta(5, 2)  # Higher credibility
    
    # Generate engagement metrics
    base_engagement = user["followers"] * 0.01
    
    if is_misinformation:
        # Misinformation often gets more engagement
        engagement_multiplier = np.random.uniform(1.5, 3.0)
    else:
        engagement_multiplier = np.random.uniform(0.5, 1.5)
    
    likes = int(base_engagement * engagement_multiplier * np.random.exponential(1))
    shares = int(likes * np.random.uniform(0.1, 0.5))
    comments = int(likes * np.random.uniform(0.05, 0.2))
    
    return {
        "post_id": f"P{post_id:08d}",
        "user_id": user["user_id"],
        "timestamp": (datetime(2024, 6, 1) + timedelta(
            hours=random.randint(0, 180 * 24)  # 6 months
        )).isoformat(),
        "content_type": np.random.choice(["text", "image", "video", "link"]),
        "topic": topic,
        "text_length": int(np.random.lognormal(4, 1)),
        "has_media": np.random.random() < 0.4,
        "likes": likes,
        "shares": shares,
        "comments": comments,
        "is_misinformation": is_misinformation,
        "misinfo_type": misinfo_type,
        "credibility_score": round(credibility, 3),
        "hashtags": random.sample([f"#{t}" for t in TOPICS], k=random.randint(0, 3)),
        "mentions": [f"@user_{random.randint(1, NUM_USERS)}" for _ in range(random.randint(0, 3))]
    }


def generate_fact_check(fact_id: int) -> Dict:
    """Generate a fact-check entry"""
    topic = random.choice(TOPICS)
    
    verdict = np.random.choice(
        ["true", "false", "mixed", "unverified"],
        p=[0.3, 0.4, 0.2, 0.1]
    )
    
    return {
        "fact_id": f"FC{fact_id:06d}",
        "claim": f"Sample claim about {topic} #{fact_id}",
        "verdict": verdict,
        "topic": topic,
        "source": np.random.choice([
            "Snopes", "PolitiFact", "FactCheck.org", 
            "Reuters Fact Check", "AP Fact Check"
        ]),
        "published_date": (datetime(2024, 1, 1) + timedelta(
            days=random.randint(0, 180)
        )).isoformat(),
        "related_keywords": random.sample(TOPICS, k=random.randint(1, 3)),
        "confidence": round(np.random.beta(8, 2), 3),
        "url": f"https://factcheck.example.com/{fact_id}"
    }


def generate_cascade(cascade_id: int, posts: List[Dict], users: List[Dict]) -> Dict:
    """Generate an information cascade"""
    # Select a seed post
    seed_post = random.choice(posts)
    
    # Determine cascade type
    is_misinformation = seed_post["is_misinformation"]
    
    # Generate cascade size (misinformation tends to spread more)
    if is_misinformation:
        cascade_size = int(np.random.lognormal(4, 2))
    else:
        cascade_size = int(np.random.lognormal(3, 1.5))
    
    cascade_size = min(cascade_size, 10000)
    cascade_size = max(1, cascade_size)  # At least 1 event
    
    # Generate cascade timeline
    seed_time = datetime.fromisoformat(seed_post["timestamp"])
    
    reshare_events = []
    current_users = {seed_post["user_id"]}
    event_time = seed_time  # Initialize to seed time
    
    for i in range(cascade_size):
        # Exponential growth pattern
        time_offset = timedelta(minutes=np.random.exponential(30) * (i + 1))
        event_time = seed_time + time_offset
        
        # Select resharing user
        if current_users and np.random.random() < 0.7:
            # Reshare from existing cascade participant
            source_user = random.choice(list(current_users))
        else:
            # New user joins cascade
            source_user = random.choice(users)["user_id"]
        
        target_user = random.choice(users)["user_id"]
        
        reshare_events.append({
            "event_id": f"E{cascade_id:06d}_{i:04d}",
            "timestamp": event_time.isoformat(),
            "source_user": source_user,
            "target_user": target_user,
            "depth": min(i // 10, 10),  # Cascade depth
            "platform": np.random.choice(["twitter", "facebook", "reddit", "other"])
        })
        
        current_users.add(target_user)
    
    # Calculate cascade metrics
    duration_hours = (event_time - seed_time).total_seconds() / 3600
    
    return {
        "cascade_id": f"C{cascade_id:06d}",
        "seed_post_id": seed_post["post_id"],
        "seed_user_id": seed_post["user_id"],
        "topic": seed_post["topic"],
        "is_misinformation": is_misinformation,
        "misinfo_type": seed_post["misinfo_type"],
        "total_reshares": cascade_size,
        "unique_users": len(current_users),
        "duration_hours": round(duration_hours, 2),
        "max_depth": max(e["depth"] for e in reshare_events) if reshare_events else 0,
        "events": reshare_events[:100],  # Store first 100 events
        "early_detection_label": is_misinformation  # Ground truth for early detection
    }


def main():
    """Generate all data files"""
    print("Generating GraphFlood social network data...")
    
    # Create directories
    os.makedirs("data/graph", exist_ok=True)
    os.makedirs("data/posts", exist_ok=True)
    os.makedirs("data/factchecks", exist_ok=True)
    os.makedirs("data/cascades", exist_ok=True)
    os.makedirs("data/metadata", exist_ok=True)
    
    # Generate users
    print("Generating users...")
    users = []
    for i in range(1, NUM_USERS + 1):
        if i % 10000 == 0:
            print(f"  Generated {i}/{NUM_USERS} users...")
        users.append(generate_user(i))
    
    # Save users
    print("Saving users...")
    users_df = pd.DataFrame(users)
    users_df.to_csv("data/graph/users.csv", index=False)
    
    # Generate social graph (reduced for performance)
    print("Generating social graph...")
    # For performance, generate a subset of edges
    edges = []
    for i, user in enumerate(users[:10000]):  # First 10K users
        if i % 1000 == 0:
            print(f"  Processing user {i}/10000...")
        
        num_following = min(user["following"], 100)
        following_indices = random.sample(range(len(users)), min(num_following, len(users)))
        
        for idx in following_indices:
            if idx != i:
                edges.append({
                    "follower": user["user_id"],
                    "following": users[idx]["user_id"]
                })
    
    edges_df = pd.DataFrame(edges)
    edges_df.to_csv("data/graph/edges.csv", index=False)
    
    # Generate posts
    print("Generating posts...")
    posts = []
    for i in range(1, NUM_POSTS + 1):
        if i % 5000 == 0:
            print(f"  Generated {i}/{NUM_POSTS} posts...")
        posts.append(generate_post(i, users))
    
    posts_df = pd.DataFrame(posts)
    posts_df.to_csv("data/posts/posts.csv", index=False)
    
    # Generate fact-checks
    print("Generating fact-checks...")
    fact_checks = []
    for i in range(1, NUM_FACT_CHECKS + 1):
        if i % 1000 == 0:
            print(f"  Generated {i}/{NUM_FACT_CHECKS} fact-checks...")
        fact_checks.append(generate_fact_check(i))
    
    fact_checks_df = pd.DataFrame(fact_checks)
    fact_checks_df.to_csv("data/factchecks/fact_checks.csv", index=False)
    
    # Generate cascades
    print("Generating cascades...")
    cascades = []
    for i in range(1, NUM_CASCADES + 1):
        if i % 500 == 0:
            print(f"  Generated {i}/{NUM_CASCADES} cascades...")
        cascades.append(generate_cascade(i, posts, users))
    
    with open("data/cascades/cascades.json", "w") as f:
        json.dump({"cascades": cascades}, f, indent=2)
    
    # Generate metadata
    metadata = {
        "generated_date": datetime.now().isoformat(),
        "num_users": NUM_USERS,
        "num_edges": len(edges),
        "num_posts": NUM_POSTS,
        "num_fact_checks": NUM_FACT_CHECKS,
        "num_cascades": NUM_CASCADES,
        "misinformation_rate": sum(1 for p in posts if p["is_misinformation"]) / NUM_POSTS,
        "topics": TOPICS,
        "user_types": [ut["type"] for ut in USER_TYPES]
    }
    
    with open("data/metadata/dataset_info.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("\nData generation complete!")
    print(f"  Users: {NUM_USERS}")
    print(f"  Edges: {len(edges)}")
    print(f"  Posts: {NUM_POSTS}")
    print(f"  Fact-checks: {NUM_FACT_CHECKS}")
    print(f"  Cascades: {NUM_CASCADES}")
    print(f"  Misinformation rate: {metadata['misinformation_rate']*100:.1f}%")


if __name__ == "__main__":
    main()
