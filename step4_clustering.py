import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

user_movie_matrix = pd.read_pickle('user_movie_matrix.pkl')
print("Matrix loaded!")

inertia = []
K = range(1, 11)
for k in K:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(user_movie_matrix)
    inertia.append(km.inertia_)

plt.figure(figsize=(8, 4))
plt.plot(K, inertia, 'bo-')
plt.xlabel('Number of Clusters K')
plt.ylabel('Inertia')
plt.title('Elbow Method - Finding Best K')
plt.grid(True)
plt.savefig('elbow_curve.png')
plt.show()
print("Elbow curve saved!")

kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
user_movie_matrix['cluster'] = kmeans.fit_predict(user_movie_matrix)
print("Clustering done!")
print("Users per cluster:")
print(user_movie_matrix['cluster'].value_counts())

pca = PCA(n_components=2)
coords = pca.fit_transform(user_movie_matrix.drop('cluster', axis=1))

plt.figure(figsize=(8, 6))
colors = ['red', 'blue', 'green', 'orange', 'purple']
for i in range(5):
    mask = user_movie_matrix['cluster'] == i
    plt.scatter(coords[mask, 0], coords[mask, 1],
                c=colors[i], label=f'Cluster {i}', alpha=0.6)
plt.title('User Clusters (PCA Visualization)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend()
plt.savefig('clusters_pca.png')
plt.show()
print("PCA plot saved!")

user_movie_matrix.to_pickle('user_movie_matrix_clustered.pkl')
print("Saved! All done.")