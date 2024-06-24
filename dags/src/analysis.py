import pandas as pd
import os
from scipy.spatial.distance import cosine
from src.logger import make_logger
log = make_logger("pipeline")


class DatasetAnalyzer:
    def __init__(self) -> None:
        self.users_df = pd.read_csv(
            "dags/dataset/u.user",
            delimiter="|",
            header=None,
            names=["userid", "age", "gender", "occupation", "zipcode"],
        )
        item_cols = [
            "movie_id",
            "title",
            "release date",
            "video release date",
            "IMDb URL",
            "unknown",
            "Action",
            "Adventure",
            "Animation",
            "Children's",
            "Comedy",
            "Crime",
            "Documentary",
            "Drama",
            "Fantasy",
            "Film-Noir",
            "Horror",
            "Musical",
            "Mystery",
            "Romance",
            "Sci-Fi",
            "Thriller",
            "War",
            "Western",
        ]
        self.items_df = pd.read_csv(
            "dags/dataset/u.item",
            header=None,
            delimiter="|",
            names=item_cols,
            encoding="latin-1",
        )
        self.ratings_df = pd.read_csv(
            "dags/dataset/u.data",
            header=None,
            delimiter="\t",
            names=["userid", "itemid", "rating", "timestamp"],
        )

    def get_occupation_mean_age(self):
        return self.users_df.groupby("occupation")["age"].mean()

    def get_top_n_movies(self, n, threshold):
        item_ratings = self.ratings_df.groupby("itemid").agg(
            mean_rating=("rating", "mean"), rating_count=("rating", "count")
        )
        filtered_items = item_ratings[item_ratings["rating_count"] >= threshold]
        top_n_items = filtered_items.sort_values(
            by="mean_rating", ascending=False
        ).head(n)
        return top_n_items

    def get_top_genres_occupation_and_age_group(self):
        # Define age groups
        bins = [20, 25, 35, 45, float("inf")]
        labels = ["20-25", "25-35", "35-45", "45 and older"]
        self.users_df["age_group"] = pd.cut(
            self.users_df["age"], bins, labels=labels, right=False
        )

        # Merge DataFrames
        merged_df = self.ratings_df.merge(
            self.users_df, left_on="userid", right_on="userid"
        )
        merged_df = merged_df.merge(
            self.items_df, left_on="itemid", right_on="movie_id"
        )

        # Melt items_df to have one row per movie-genre pair
        genres = self.items_df.columns[5:]
        items_melted = pd.melt(
            self.items_df,
            id_vars=["movie_id", "title", "release date"],
            value_vars=genres,
            var_name="genre",
            value_name="is_genre",
        )
        items_melted = items_melted[items_melted["is_genre"] == 1]

        # Merge the melted items with the merged_df
        merged_df = merged_df.merge(
            items_melted[["movie_id", "genre"]], left_on="itemid", right_on="movie_id"
        )
        # Group by age_group, occupation, and genre, then calculate the mean rating
        grouped_df = (
            merged_df.groupby(["age_group", "occupation", "genre"])["rating"]
            .mean()
            .reset_index()
            .dropna()
        )

        # Find the top genre for each occupation in each age group and sort
        top_genres = grouped_df.loc[
            grouped_df.groupby(["age_group", "occupation"], observed=True)[
                "rating"
            ].idxmax()
        ]
        top_genres = top_genres.sort_values(by=["age_group", "occupation"]).reset_index(
            drop=True
        )

        return top_genres
    
    def movie_similarity(self,movie1, movie2):
        # Get ratings for the two movies
        ratings1 = self.ratings_matrix[movie1]
        ratings2 = self.ratings_matrix[movie2]
        
        # Drop NaN values (users who haven't rated both movies)
        common_users = ratings1.dropna().index.intersection(ratings2.dropna().index)
        
        # Calculate cosine similarity
        if len(common_users) < 2:  # Adjust this threshold based on your co-occurrence requirement
            return 0, len(common_users)
        
        sim = 1 - cosine(ratings1[common_users], ratings2[common_users])
        
        return sim, len(common_users)

    def find_similar_movies(self, movie_id, top_n=10, similarity_threshold=0.95, co_occurrence_threshold=50):
        similarities = []
    
        # Get movie title based on movie_id
        movie_title = self.items_df[self.items_df['movie_id'] == movie_id]['title'].values[0]

        self.ratings_matrix = self.ratings_df.pivot_table(index='userid', columns='itemid', values='rating')
        
        for other_movie_id in self.ratings_matrix.columns:
            if other_movie_id != movie_id:
                sim, co_occurrence = self.movie_similarity(movie_id, other_movie_id)
                
                if sim >= similarity_threshold and co_occurrence >= co_occurrence_threshold:
                    other_movie_title = self.items_df[self.items_df['movie_id'] == other_movie_id]['title'].values[0]
                    similarities.append((other_movie_title, sim, co_occurrence))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return movie_title, similarities[:top_n]
