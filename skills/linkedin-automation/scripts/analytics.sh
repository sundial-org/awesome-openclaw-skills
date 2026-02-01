#!/bin/bash
# LinkedIn Analytics Script
# Usage: ./analytics.sh [--days 7]

DAYS="${1:-7}"

cat << EOF
📊 LINKEDIN ANALYTICS WORKFLOW
═══════════════════════════════════════

Fetch engagement data for the last $DAYS days.

Steps to execute via browser tool:

1. Navigate to https://www.linkedin.com/analytics/creator/

2. Extract dashboard metrics:
   - Impressions (total views)
   - Engagements (likes + comments + shares)
   - Profile views
   - Follower count
   - Search appearances

3. Navigate to posts section to get per-post stats:
   - URL: https://www.linkedin.com/in/me/recent-activity/all/
   - For each post, extract:
     - Post date
     - Impressions
     - Reactions count
     - Comments count
     - Reposts count

4. Calculate metrics:
   - Engagement rate = (reactions + comments + reposts) / impressions * 100
   - Average engagement per post
   - Best performing post (highest engagement rate)
   - Best posting time (based on top performers)

5. Return structured data:
   {
     "period": "$DAYS days",
     "totalImpressions": <number>,
     "totalEngagements": <number>,
     "engagementRate": "<percentage>",
     "followerChange": "<+/- number>",
     "topPost": {
       "content": "<preview>",
       "impressions": <number>,
       "engagementRate": "<percentage>"
     },
     "posts": [...]
   }

💡 Tip: Run weekly to track trends
EOF
