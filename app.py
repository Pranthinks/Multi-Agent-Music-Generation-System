from flask import Flask, render_template, request, jsonify, send_file
from agent_langchain import create_langchain_multiagent_system, load_database
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Initialize LangChain multi-agent system
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file!")
    exit(1)

print("\nInitializing LangChain Multi-Agent System...")
agent_system = create_langchain_multiagent_system(api_key)
print("System ready!\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        result = agent_system.invoke({"input": user_input})
        
        return jsonify({
            'response': result['output'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        db = load_database()
        customers = db.get("customers", {})
        
        customer_list = []
        for name, data in customers.items():
            customer_list.append({
                'name': name,
                'status': data.get('status', 'inactive'),
                'payments': len(data.get('payments', [])),
                'last_payment': data.get('last_payment', 'Never')
            })
        
        return jsonify({'customers': customer_list})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music-files', methods=['GET'])
def get_music_files():
    try:
        music_dir = "generated_music"
        
        if not os.path.exists(music_dir):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(music_dir):
            if filename.endswith('.mp3') and '_sample_' not in filename:
                filepath = os.path.join(music_dir, filename)
                file_stat = os.stat(filepath)
                
                files.append({
                    'name': filename,
                    'path': filepath,
                    'size': round(file_stat.st_size / 1024, 2),  # KB
                    'created': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'files': files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/play-music', methods=['GET'])
def play_music():
    try:
        file_path = request.args.get('file', '')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Security check: ensure the file is in the generated_music directory
        if not file_path.startswith('generated_music'):
            return jsonify({'error': 'Invalid file path'}), 403
        
        return send_file(file_path, mimetype='audio/mpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    try:
        data = request.json
        action = data.get('action', '')
        
        actions = {
            'generate_happy': "Generate a happy, uplifting song about sunshine",
            'generate_sad': "Generate a sad, melancholic song about rain",
            'generate_energetic': "Generate an energetic, powerful track for motivation",
            'check_status': "List all customers and their subscription status",
            'post_social': "Post our latest music to social media with an engaging caption"
        }
        
        if action not in actions:
            return jsonify({'error': 'Invalid action'}), 400
        
        result = agent_system.invoke({"input": actions[action]})
        
        return jsonify({
            'response': result['output'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)