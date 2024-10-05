from flask import Flask, render_template, request, jsonify, make_response
from model import add_interaction, build_model
import uuid  # To generate a unique user ID

app = Flask(__name__)

# Serve the main HTML page
@app.route('/')
def home():
    # Check if the user has a cookie; if not, set a unique user ID
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        user_id = str(uuid.uuid4())  # Generate a new unique user ID
        resp = make_response(render_template('index.html'))
        resp.set_cookie('user_id', user_id, max_age=60*60*24*365)  # Cookie expires in 1 year
        return resp
    else:
        return render_template('index.html')

# Route to track user interactions
@app.route('/track', methods=['POST'])
def track_interaction():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        user_id = request.cookies.get('user_id')  # Retrieve the user's ID from the cookie
        if not user_id:
            return jsonify({"error": "No user ID found"}), 400
        
        article_title = data.get('title')
        category = data.get('category')
        description = data.get('description')
        
        if not all([article_title, category, description]):
            return jsonify({"error": "Incomplete data received"}), 400
        
        # Log the interaction for debugging
        app.logger.info(f"Tracking interaction for user_id={user_id}: {article_title}, {category}, {description}")
        
        # Add interaction to the model, using the user's ID from the cookie
        add_interaction(user_id, article_title, category, description)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        app.logger.error(f"Error in /track route: {e}")
        return jsonify({"error": str(e)}), 500

# Route to fetch personalized recommendations
@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        user_id = request.cookies.get('user_id')  # Get user ID from the cookie
        if not user_id:
            return jsonify({"error": "No user ID found"}), 400
        
        # Fetch personalized recommendations based on the user's ID
        recommendations = build_model(user_id)
        
        if not recommendations:
            return jsonify({"message": "No recommendations available"}), 200
        
        return jsonify(recommendations), 200
    except Exception as e:
        app.logger.error(f"Error in /recommend route: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
