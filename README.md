# FlickFindr: Dual-Industry Machine Learning Recommendation Engine

**FlickFindr** is an advanced, full-stack movie recommendation platform built with Python and Streamlit. Serving a database of over 9,700+ movies and analyzing 100,000+ user ratings, the engine provides hyper-personalized content suggestions across both Hollywood and Bollywood cinematic landscapes.

Beyond standard content-based filtering, this project implements a robust machine learning pipeline utilizing Singular Value Decomposition (SVD), K-Means Clustering, and Principal Component Analysis (PCA) to map user-item matrices and deliver highly accurate, latent-feature recommendations.

Live Dashboard Link: [View Live App](https://movie-recommender-cc3aw56j6jvqomrwgw8gmc.streamlit.app) *(Update if necessary)*

---

## 🚀 Key Features

* **Dual-Industry Catalog:** Dynamic UI toggles instantly switch the backend querying state between Bollywood and Hollywood datasets.
* **Advanced ML Pipeline:** Utilizes SVD for collaborative filtering and PCA-backed clustering for latent feature extraction, moving beyond simple cosine similarity.
* **User State Management:** Implements local authentication and history tracking mechanisms via integrated JSON architectures (`users.json`, `history.json`).
* **Interactive Metadata Routing:** Dynamically fetches and renders high-quality movie poster art, ratings out of 10, and clickable anchor tags that route directly to official IMDb profiles.
* **High-Performance UI:** Built on Streamlit with a custom dark-theme layout, metrics dashboards, and responsive poster grids.

---

## 📂 Repository Structure & ML Pipeline

The project is built as a step-by-step pipeline, one script per stage:

```text
├── Data & Models/            
│   ├── all_movies.csv / ratings.csv    # Raw TMDB & User rating datasets
│   ├── cleaned_data.csv                # Post-ETL normalized data
│   ├── *_similarity.pkl                # Pre-computed Cosine/SVD similarity matrices
│   ├── user_movie_matrix.pkl           # Sparse matrix for collaborative filtering
│   └── clusters_pca.png                # Visualized PCA variance & clustering curves
├── Pipeline Scripts/         
│   ├── step2_preprocessing.py          # Data cleaning, null-handling, and ETL operations
│   ├── step3_model.py                  # Core content-based vectorization modeling
│   ├── step4_clustering.py             # K-Means clustering and PCA dimensionality reduction
│   ├── step6_reduce.py                 # Matrix size optimization for deployment
│   ├── step8_bollywood_model.py        # Isolated model training for Hindi cinema
│   ├── step9_svd.py                    # Singular Value Decomposition for latent feature mapping
│   └── step10_login.py                 # User authentication and session state logic
├── step5_app.py                        # Main Streamlit application entry point
├── users.json / history.json           # Local database for user session tracking
└── requirements.txt                    # Python dependencies

🛠️ Installation & Local Execution
1. Clone the Workspace
Bash
git clone [https://github.com/athrvaraut/movie-recommender.git](https://github.com/athrvaraut/movie-recommender.git)
cd movie-recommender
2. Environment Setup
Ensure you have Python 3.10+ installed locally. Install the required data science and web libraries:

Bash
pip install -r requirements.txt
3. Launch the Application Locally
Spin up the local Streamlit server to interact with the FlickFindr UI:

Bash
streamlit run step5_app.py
(Note: If your main app execution file is vscodemoviereccomender.py, run that instead).

🧠 Technical Architecture
Dimensionality Reduction & Clustering (step4_clustering.py): Reduces the massive sparse matrix of user ratings using PCA, allowing for efficient K-Means clustering to group similar user profiles without exhausting memory.

Matrix Factorization (step9_svd.py): Employs SVD to uncover latent dimensions (hidden genres or features) that explain user preferences, resulting in a more nuanced svd_similarity.pkl model.

Optimized Deployment (step6_reduce.py): Web-based Streamlit environments have strict memory limits. This pipeline includes explicit reduction scripts to compress .pkl files, ensuring the live cloud app does not crash during cold starts.
