import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

cleaned = pd.read_csv('cleaned_data.csv')

popular = cleaned['title'].value_counts()
popular_movies = popular[popular >= 50].index.tolist()
print("Popular movies:", len(popular_movies))

user_movie_matrix = pd.read_pickle('user_movie_matrix.pkl')
filtered_matrix = user_movie_matrix[popular_movies]

similarity = cosine_similarity(filtered_matrix.T)
similarity_df = pd.DataFrame(
    similarity,
    index=popular_movies,
    columns=popular_movies
)

similarity_df.to_pickle('movie_similarity_small.pkl')
print("Saved! Size reduced.")
print("New shape:", similarity_df.shape)