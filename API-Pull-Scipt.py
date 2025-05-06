API_KEY = ""

import time
import json
import pandas as pd
from googleapiclient.discovery import build

youtube = build("youtube", "v3", developerKey=API_KEY)

def load_creator_ids(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_channel_stats(channel_id):
    # Now requesting snippet to get the channel's title
    res = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    ).execute()
    items = res.get("items", [])
    if not items:
        raise ValueError(f"No channel found for ID {channel_id}")

    # extract channel name
    snippet = items[0]["snippet"]
    channel_name = snippet.get("title", "")

    # extract stats
    stats = items[0]["statistics"]
    subs = int(stats.get("subscriberCount", 0))
    total_videos = int(stats.get("videoCount", 0))

    # uploads playlist
    uploads_pl = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    return channel_name, subs, total_videos, uploads_pl

def get_video_ids(playlist_id, max_results=20): # YOU NEED TO CHANGE THIS ONE TOO
    try:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=max_results
        ).execute()
        return [item["contentDetails"]["videoId"] for item in res.get("items", [])]
    except Exception as e:
        print(f"  ⚠️  Skipping playlist {playlist_id}: {e}")
        return []  # empty list means this creator gets skipped

def get_video_details(video_ids):
    res = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    ).execute()

    videos = []
    for item in res.get("items", []):
        snip   = item["snippet"]
        stats  = item.get("statistics", {})
        cont   = item["contentDetails"]
        view   = int(stats.get("viewCount", 0))
        like   = int(stats.get("likeCount", 0))
        comment= int(stats.get("commentCount", 0))

        videos.append({
            "videoId":          item["id"],
            "title":            snip.get("title", ""),
            "publishedAt":      snip.get("publishedAt"),
            "duration":         cont.get("duration"),
            "viewCount":        view,
            "likeCount":        like,
            "commentCount":     comment,
            "likesToViews":     like / view if view > 0 else 0,
            "commentsToViews":  comment / view if view > 0 else 0,
            "likesToComments":  like / comment if comment > 0 else 0
        })

    time.sleep(0.1)
    return videos

# 1) Load creator IDs
creator_ids = load_creator_ids("")

data = {}
metrics_list = []
temp_counter = 0

for cid in creator_ids:
    try:
        # now also getting the channel_name
        channel_name, subs, total_videos, uploads_pl = get_channel_stats(cid)
    except Exception as e:
        print(f"Skipping {cid}: {e}")
        continue

    # fetch last 10 video IDs & details
    video_ids  = get_video_ids(uploads_pl, max_results=20) # YOU NEED TO CHANGE THIS ONE TOO
    video_data = get_video_details(video_ids)
    if not video_data:
        print(f"No videos for {cid}")
        continue

    # DataFrame for computing metrics
    df_v = pd.DataFrame(video_data)
    df_v["publishedAt"] = pd.to_datetime(df_v["publishedAt"], utc=True)
    df_v = df_v.sort_values("publishedAt")

    if len(df_v) < 3:
        print(f"Skipping {cid}: only {len(df_v)} videos (< 3 required)")
        continue

    # compute intervals
    diffs = df_v["publishedAt"].diff().dt.total_seconds() / 86400
    avg_interval = diffs.iloc[1:].mean()
    std_interval = diffs.iloc[1:].std(ddof=1)

    # compute viewership change
    view_diffs      = df_v["viewCount"].diff().fillna(0)
    avg_view_change = view_diffs.iloc[1:].mean()

    # videos in the last year
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=365)
    videos_last_year = int((df_v["publishedAt"] >= cutoff).sum())

    # collect raw metrics
    metrics_list.append({
        "creatorId":                   cid,
        "creatorName":                 channel_name,
        "videos_last_year":            videos_last_year,
        "avg_views_per_video":         df_v["viewCount"].mean(),
        "avg_like_to_view_ratio":      df_v["likesToViews"].mean(),
        "avg_comment_to_view_ratio":   df_v["commentsToViews"].mean(),
        "avg_upload_interval_days":    avg_interval,
        "std_upload_interval_days":    std_interval,
        "theta_upload_interval":       std_interval / avg_interval if avg_interval else 0
    })

    # initialize JSON entry
    data[cid] = {
        "creatorName":               channel_name,
        "influencer":                None,    # to be filled later
        "noOfSubscribers":           subs,
        "totalVideos":               total_videos,
        "averageTimeBetweenUploads": avg_interval,
        "uploadStandardDeviation":   std_interval,
        "averageChangeInViewership": avg_view_change,
        "videos":                    video_data
    }
    temp_counter += 1
    print(temp_counter)

# 2) Score *without* normalization
#    Weights now refer to the raw metrics
weights = {
    "avg_views_per_video":        0.40,
    "avg_like_to_view_ratio":     0.30,
    "avg_comment_to_view_ratio":  0.20,
    "avg_upload_interval_days":   0.25,
    "theta_upload_interval":      0.15
}
threshold = 1

# Iterate over your collected metrics_list (each is a dict)
for m in metrics_list:
    cid = m["creatorId"]

    # compute weighted sum on raw values
    score = (
        m["avg_views_per_video"]       * weights["avg_views_per_video"]         * 1/100000  +
        m["avg_like_to_view_ratio"]    * weights["avg_like_to_view_ratio"]      * 1/0.07    +
        m["avg_comment_to_view_ratio"] * weights["avg_comment_to_view_ratio"]   * 1/0.005   +
        m["avg_upload_interval_days"]  * weights["avg_upload_interval_days"]    * -1/30     +
        m["theta_upload_interval"]     * weights["theta_upload_interval"]       * -1
    )

    # apply threshold AND at least 6 videos last year
    is_influencer = int(score >= threshold and m["videos_last_year"] >= 6)
    data[cid]["influencer"] = is_influencer

# 3) Write out JSON as before
with open("", "w") as f:
    json.dump(data, f, indent=2)
print("✅ Saved")
