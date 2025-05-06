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

# Instructions to Execute

When running the program in collab, the user need to install torch-geometric and captum, however due to collab version conflicts some errors will be encountered in the process. please execute as follows:

Step 1: run the first code block with the line "!pip install captum" NOT commented out. This should raise an error at the end.

Step 2: Open runtime and restart the session.

Step 3: Comment out "!pip install captum" and run the first block again to ensure torch-geometric has been installed.

Step 4: Run the block to import all of the necessary libraries.

Step 5: Run the next block for uploading the JSON and upload a JSON file of the dataset *NOTICE: The dataset MUST be named new_target_file_plus_266.json for the rest of the program to work.

Step 6: Go through the rest of the code blocks from top to bottom executing. Keep in mind that the final block for creating the captum graph takes about 40-45 minutes to execute with the dataset.
