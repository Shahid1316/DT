import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# DataFrame to store user interactions (In-memory storage)
user_interactions = pd.DataFrame(columns=['user_id', 'article_title', 'category', 'description'])

# Function to add a user's interaction to the dataset
def add_interaction(user_id, article_title, category, description):
    global user_interactions
    
    # Create a new interaction entry
    new_interaction = pd.DataFrame([{
        'user_id': user_id,
        'article_title': article_title,
        'category': category,
        'description': description
    }])
    
    # Append the new interaction to the DataFrame
    user_interactions = pd.concat([user_interactions, new_interaction], ignore_index=True)
    print(f"Updated interactions: {user_interactions}")

# Function to build and return personalized recommendations for a user
def build_model(user_id):
    # Filter interactions for the specific user
    user_data = user_interactions[user_interactions['user_id'] == user_id]
    
    # If no data for the user, return an empty list
    if user_data.empty:
        print(f"No interactions found for user_id={user_id}")
        return []
    
    print(f"Generating recommendations for user_id={user_id}")

    # Use TF-IDF to create article similarity
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(user_data['description'])

    # Compute cosine similarity matrix for articles the user interacted with
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Get indices of articles sorted by similarity (most similar to least)
    similar_indices = cosine_sim.argsort().flatten()[::-1]
    
    # Extract titles and categories for the most similar articles
    similar_items = [(user_data.iloc[i]['article_title'], user_data.iloc[i]['category']) 
                     for i in similar_indices if i < len(user_data)]
    
    return similar_items[:5]
 