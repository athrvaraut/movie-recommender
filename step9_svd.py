import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
import pickle

df = pd.read_csv('cleaned_data.csv')
print("Loaded cleaned data:", df.shape)

user_movie_matrix = pd.read_pickle('user_movie_matrix.pkl')
print("Matrix shape:", user_movie_matrix.shape)

matrix = user_movie_matrix.values
user_ratings_mean = np.mean(matrix, axis=1)
matrix_demeaned = matrix - user_ratings_mean.reshape(-1, 1)

print("Applying SVD...")
U, sigma, Vt = svds(matrix_demeaned, k=50)
sigma = np.diag(sigma)

predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
predicted_df = pd.DataFrame(
    predicted_ratings,
    index=user_movie_matrix.index,
    columns=user_movie_matrix.columns
)
print("SVD predictions done!")

movie_similarity_svd = cosine_similarity(predicted_df.T)
movie_similarity_svd_df = pd.DataFrame(
    movie_similarity_svd,
    index=user_movie_matrix.columns,
    columns=user_movie_matrix.columns
)

popular = df['title'].value_counts()
popular_movies = popular[popular >= 50].index.tolist()
svd_small = movie_similarity_svd_df.loc[
    movie_similarity_svd_df.index.isin(popular_movies),
    movie_similarity_svd_df.columns.isin(popular_movies)
]

svd_small.to_pickle('svd_similarity.pkl')
print(f"SVD matrix saved! Shape: {svd_small.shape}")
print("Top 5 movies similar to Toy Story (1995) using SVD:")
if 'Toy Story (1995)' in svd_small.columns:
    similar = svd_small['Toy Story (1995)'].sort_values(ascending=False).drop('Toy Story (1995)')
    print(similar.head(5))
print("Done! svd_similarity.pkl created.")