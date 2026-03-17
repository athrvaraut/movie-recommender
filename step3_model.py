import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

user_movie_matrix = pd.read_pickle('user_movie_matrix.pkl')
print("Matrix loaded! Shape:", user_movie_matrix.shape)

movie_similarity = cosine_similarity(user_movie_matrix.T)
movie_similarity_df = pd.DataFrame(
    movie_similarity,
    index=user_movie_matrix.columns,
    columns=user_movie_matrix.columns
)
print("Similarity matrix built!")

def recommend_movies(movie_name, n=5):
    if movie_name not in movie_similarity_df.columns:
        print("Movie not found!")
        return []
    similar = movie_similarity_df[movie_name].sort_values(ascending=False)
    similar = similar.drop(movie_name)
    top = similar.head(n)
    return top

print("\nRecommendations for Toy Story (1995):")
results = recommend_movies("Toy Story (1995)", n=5)
print(results)

print("\nRecommendations for Jumanji (1995):")
results2 = recommend_movies("Jumanji (1995)", n=5)
print(results2)

movie_similarity_df.to_pickle('movie_similarity.pkl')
print("Saved! movie_similarity.pkl created.")