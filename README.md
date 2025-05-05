# Using-GraphSAGE-to-Classify-YouTuber-Influencer-Status

RQ: Can you predict whether an creator is an “influencer” based on the continuous positive interactions throughout their videos?

Motivation: Companies looking to acquire more customers and are willing to sponsor. To do so they need to know who the best individuals to sponsor would be to maximize new customers from that sponsorship. With this in mind, we will be searching for a way to determine accounts that have the potential to become "important" early on, thereby giving the sponsor more exposure.​

Results were collected from two different combinations of features:
We had a set (A) with the features: 
Average Likes
Average Subscribers per Like
Average Likes per Comment
Average Like per View
Average Like Growth
Average Days Between Upload
A set (B) that also included:
Subscriber Count
Average Views
Average Comments
Average number of videos

We ran the model 10 Times for each set.

For Set A:

Average Accuracy: 0.58446

Average F1 Score: 0.51863

For Set B:

Average Accuracy: 0.70074

Average F1 Score: 0.68088

