# -*- coding: utf-8 -*-
"""Movie Recommender System : Minor Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1swCmQpietWTSYOU-3lZGFXf6jpkhz54K

Recommender Systems are a class of AI systems that predict and recommend new items 
(e.g. YouTube videos, Netflix shows, Amazon products).


Here's what we need to do:
* Step 1: Get a dataset of movie ratings, and make sure we understand how the dataset is structured.
* Step 2: Try to get just a non-personalized set of recommendations for different users say User1 and User2, to see if we can find a movie to watch that way.
* Step 3: Get personalized ratings for User1 and User2, and import them into the system in the correct format.
* Step 4: Train a User-User collaborative filtering model to provide personalized recommendations based on User1 and User2 prior ratings.
* Step 5: Combine ratings to generate a single ranked recommendation list.

We'll use an existing dataset published by MovieLens, which contains about 100,000 user ratings for about 10,000 different movies.

We'll also use the LensKit API to implement our recommender systems algorithms.

***STEP 1***

**Step 1.1**
"""

!pip install lenskit
!pip install -U numba

import lenskit.datasets as ds
import pandas as pd

!git clone https://github.com/crash-course-ai/lab4-recommender-systems.git

data = ds.MovieLens('lab4-recommender-systems/')

print("Successfully installed dataset.")

"""It's important to understand how a dataset is structured and to make sure that the dataset imported correctly.  Let's print out a few rows of the rating data. 

As you see, MovieLens stores a user's ID number (the first row few rows look like they're all ratings from user 1), the item's ID (in this case each ID is a different movie), the rating the user gave this item, and a time stamp for when the rating was left.

**Step 1.2**
"""

# Top 10 "ratings" of the MovieLens files
rows_to_show = 10   
data.ratings.head(rows_to_show)

"""A big aspect of recommender system datasets is how they handle missing data. Recommender systems usually have a LOT of missing data, because most users only rate a few movies and most movies only receive ratings from a few users. 

For example, we can see that user #1 provided rating of 4.0 to the item #1 and that they provided a rating of 4.0 to item #3. But there isn't a rating for item #2 at all, which means that user #1 never rated this item. It's helpful to know that this dataset doesn't store unranked items at all, instead of, for example, storing unranked items as 0 ratings. 

But here we have another small issue: names like item #1 and item #2 aren't very descriptive, so we can't tell what those movies are. Thankfully, MovieLens also has a data table called "movies" that includes information about titles and genres. We can get a more meaningful look at these data by joining the two data files. 

**Step 1.3**
"""

joined_data = data.ratings.join(data.movies['genres'], on='item')
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data.head(rows_to_show)

"""Now we can see the titles and genres of each item, and we'll continue using "join" before printing results.

Because we've successfully imported our ratings data and see how it's structured, we're done with Step 1.

***STEP 2***

Now that we have ratings, let's create a generic set of recommended movies by looking at the highest rated films. We can average all the ratings by item, sort the list in descending order, and print that top set of recommendations.

**Step 2.1**
"""

average_ratings = (data.ratings).groupby(['item']).mean()
sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = sorted_avg_ratings.join(data.movies['genres'], on='item')
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[1:]]

print("RECOMMENDED FOR ANYBODY:")
joined_data.head(rows_to_show)

"""That seemed like a good idea, but the results are strange... _Paper Birds_? _Bill Hicks: Revelations_? Those are pretty obscure movies. Let's see what's actually happening here."""

average_ratings = (data.ratings).groupby('item') \
       .agg(count=('user', 'size'), rating=('rating', 'mean')) \
       .reset_index()

sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = sorted_avg_ratings.join(data.movies['genres'], on='item')
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[1:]]


print("RECOMMENDED FOR ANYBODY:")
joined_data.head(rows_to_show)

"""Adding the "count" column, we can see that each of these movies was given a perfect 5.0 rating but by just ONE person. They might be good movies, but we can't be very confident in these recommendations.

To improve this list, we should try only including movies in this recommendation list if they have more than a certain number of ratings, so we can be more confident that each movie is generally good. Let's start with movies that 20 or more people rated.

**Step 2.2**
"""

minimum_to_include = 20 #<-- You can try changing this minimum to include movies rated by fewer or more people

average_ratings = (data.ratings).groupby(['item']).mean()
rating_counts = (data.ratings).groupby(['item']).count()
average_ratings = average_ratings.loc[rating_counts['rating'] > minimum_to_include]
sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = sorted_avg_ratings.join(data.movies['genres'], on='item')
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[3:]]

print("RECOMMENDED FOR ANYBODY:")
joined_data.head(rows_to_show)

"""These movies are more commonly known and we can trust that they're more popularly recommended. But these movies span a bunch of genres, so we can try narrowing the list down a bit more.

Let's try to get a list of recommendations from #User1 and #User2 favorite genres. Let's say #User2 like Action movies and #User1 prefers Romance movies.
So in addition to filtering by the number of ratings, let's also filter by a particular genre. We'll run the recommendations for an action movie fan, then for a romance movie fan.

**Step 2.3**
"""

average_ratings = (data.ratings).groupby(['item']).mean()
rating_counts = (data.ratings).groupby(['item']).count()
average_ratings = average_ratings.loc[rating_counts['rating'] > minimum_to_include]
average_ratings = average_ratings.join(data.movies['genres'], on='item')
average_ratings = average_ratings.loc[average_ratings['genres'].str.contains('Action')]

sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = sorted_avg_ratings.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[3:]]
print("RECOMMENDED FOR AN ACTION MOVIE FAN:")
joined_data.head(rows_to_show)

average_ratings = (data.ratings).groupby(['item']).mean()
rating_counts = (data.ratings).groupby(['item']).count()
average_ratings = average_ratings.loc[rating_counts['rating'] > minimum_to_include]
average_ratings = average_ratings.join(data.movies['genres'], on='item')
average_ratings = average_ratings.loc[average_ratings['genres'].str.contains('Romance')]

sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = sorted_avg_ratings.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[3:]]
print("RECOMMENDED FOR A ROMANCE MOVIE FAN:")
joined_data.head(rows_to_show)

"""There's actually one movie that's on both of these lists: _The Princess Bride_. 

So, while Step 2 produced some generic recommendations, our AI hasn't given us a satisfactory output.

***STEP 3***

Step 3 is personalizing our recommender system AI.
USER1 and USER2 each need to provide our own movie ratings as data, so we have to fill out simple spreadsheets and upload these spreadsheets.

But, we need to provide these personalized ratings in the correct format. By looking at the documentation for LensKit (https://lkpy.lenskit.org/en/stable/interfaces.html#lenskit.algorithms.Recommender.recommend), we know that we need to provide a dictionary of item-rating pairs for each person. This means that we need to import the two spreadsheets from GitHub and format the data in a way that will make sense to our AI: two dictionaries.

To test that it worked, let's also print both our ratings for _The Princess Bride_, since we know that's a movie we both watched.

**Step 3.1**
"""

import csv

jabril_rating_dict = {}
jgb_rating_dict = {}

with open("/content/lab4-recommender-systems/jabril-movie-ratings.csv", newline='') as csvfile:
  ratings_reader = csv.DictReader(csvfile)
  for row in ratings_reader:
    if ((row['ratings'] != "") and (float(row['ratings']) > 0) and (float(row['ratings']) < 6)):
      jabril_rating_dict.update({int(row['item']): float(row['ratings'])})
      
with open("/content/lab4-recommender-systems/jgb-movie-ratings.csv", newline='') as csvfile:
  ratings_reader = csv.DictReader(csvfile)
  for row in ratings_reader:
    if ((row['ratings'] != "") and (float(row['ratings']) > 0) and (float(row['ratings']) < 6)):
      jgb_rating_dict.update({int(row['item']): float(row['ratings'])})
     
print("Rating dictionaries assembled!")
print("Sanity check:")
print("\t USER1's rating for 1197 (The Princess Bride) is " + str(jabril_rating_dict[1197]))
print("\t USER2's rating for 1197 (The Princess Bride) is " + str(jgb_rating_dict[1197]))

"""***STEP 4***

In Step 4, we want to actually train a new collaborative filtering model to provide recommendations. We'll use the UserUser library from LensKit to do this. This algorithm clusters similar users based on their movie ratings, and uses those clusters to predict movie ratings for one user (in this case, we'll want that user to be USER1 or USER2).

We're guiding how the algorithm decides whether a particular group of users should be clustered together by setting a minimum and maximum neighborhood size. These parameters modify the result of the algorithm.

Really small clusters represent groups of people who aren't very similar to a lot of others. So by keeping cluster size small, we'll see more unconventional recommendations. But increasing our minimum cluster size, will probably give more conventionally popular recommendations. 

Right now, we set the minimum to 3 and the maximum to 15, so the algorithm won't define a cluster unless it has at least 3 users, and it will use the 15 closest users (at most) to make rating predictions. 

**Step 4.1**
"""

from lenskit.algorithms import Recommender
from lenskit.algorithms.user_knn import UserUser

num_recs = 10  #<---- This is the number of recommendations to generate. You can change this if you want to see more recommendations

user_user = UserUser(15, min_nbrs=3) #These two numbers set the minimum (3) and maximum (15) number of neighbors to consider. These are considered "reasonable defaults," but you can experiment with others too
algo = Recommender.adapt(user_user)
algo.fit(data.ratings)

print("Set up a User-User algorithm!")

"""Now that the system has defined clusters, we can give it our personal ratings to get the top 10 recommended movies for USER1 and USER2.

For each of us, the User-User algorithm will find a neighborhood of users similar to us based on their movie ratings. It will look at movies that these similar users have rated that we haven't seen yet. Based on their ratings, it will predict how we may rate that movie if we watched it. Finally, it will order these predictions and print them in descending order to give our "top 10."

**Step 4.2**
"""

jabril_recs = algo.recommend(-1, num_recs, ratings=pd.Series(jabril_rating_dict))  #Here, -1 tells it that it's not an existing user in the set, that we're giving new ratings, while 10 is how many recommendations it should generate

joined_data = jabril_recs.join(data.movies['genres'], on='item')      
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[2:]]
print("\n\nRECOMMENDED FOR USER2:")
joined_data

jgb_recs = algo.recommend(-1, num_recs, ratings=pd.Series(jgb_rating_dict))  #Here, -1 tells it that it's not an existing user in the set, that we're giving new ratings, while 10 is how many recommendations it should generate

joined_data = jgb_recs.join(data.movies['genres'], on='item')      
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[2:]]
print("RECOMMENDED FOR USER1:")
joined_data

"""Now, we have "top 10" lists of movies for both USER1 and USER2! Each of these only has movies that each of us hasn't watched before (or at least that we didn't rate in our personal ratings). These lists include both popular movies and more obscure ones.

That concludes Step 4 of getting personalized recommendations, but our lists don't overlap at all, so we still haven't found a movie for both of us to watch.

***STEP 5***

That brings us to Step 5, making a combined movie recommendation list. Because rating preferences are stored as numbers, we can create a hybrid!

We'll do this by creating a combined dictionary of ratings. If both of us have rated a movie, it will average our ratings. If only one of us has rated a movie, it will just add that movie to the list of preferences. This isn't a perfect strategy; it's possible that I would have hated some movie that I've never seen but USER1 rated highly. But we should get a reasonable estimate across both of our datasets.

We'll also do a quick sanity check by looking at _The Princess Bride_ again. USER2 rated it as a 4.5 (because it's awesome!!) and USER1 rated it as a 3.5, so we'd expect our combined list would have it as a 4.

**Step 5.1**
"""

combined_rating_dict = {}
for k in jabril_rating_dict:
  if k in jgb_rating_dict:
    combined_rating_dict.update({k: float((jabril_rating_dict[k]+jgb_rating_dict[k])/2)})
  else:
    combined_rating_dict.update({k:jabril_rating_dict[k]})
for k in jgb_rating_dict:
   if k not in combined_rating_dict:
      combined_rating_dict.update({k:jgb_rating_dict[k]})
      
print("Combined ratings dictionary assembled!")
print("Sanity check:")
print("\tCombined rating for 1197 (The Princess Bride) is " + str(combined_rating_dict[1197]))

"""Looks like everything checks out. So now, we have a combined dictionary that we can plug right into our User-User model to output a ranked list of new movies that we should both enjoy!

**Step 5.2**
"""

combined_recs = algo.recommend(-1, num_recs, ratings=pd.Series(combined_rating_dict))  #Here, -1 tells it that it's not an existing user in the set, that we're giving new ratings, while 10 is how many recommendations it should generate

joined_data = combined_recs.join(data.movies['genres'], on='item')      
joined_data = joined_data.join(data.movies['title'], on='item')
joined_data = joined_data[joined_data.columns[2:]]
print("\n\nRECOMMENDED FOR USER1 and USER2 HYBRID:")
joined_data

"""The number one recommendation is _[Submarine](https://www.imdb.com/title/tt1440292/)_ which is a quirky movie from 2010. If this is too obscure, we could pick a different recommendation from this list like _[True Grit](https://www.imdb.com/title/tt1403865/)_.

We could also go back to Step 4.1 and set different parameters. Setting the minimum and maximum number of neighbors to make bigger clusters (for example, a minimum of 10 and and maximum of 50) would probably yield a more well-known set of movies, but it would also be less tailored to our individual interests. The trade-off between unconventional and popular results is what really characterizes recommender systems!
"""