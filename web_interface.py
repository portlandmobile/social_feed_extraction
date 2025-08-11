from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
import json
from ai_agent import LinkedInDataExtractor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['SESSION_TYPE'] = 'filesystem'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mhtml', 'mht'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the AI agent
ai_agent = LinkedInDataExtractor()

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with file upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Check file extension
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload an MHTML file (.mhtml or .mht)', 'error')
            return redirect(url_for('index'))
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            flash(f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB', 'error')
            return redirect(url_for('index'))
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        # Get parsing method and API key
        parsing_method = request.form.get('parsing_method', 'traditional')
        openai_api_key = request.form.get('openai_api_key', '')
        
        # Initialize AI agent with API key if provided
        if parsing_method == 'ai' and openai_api_key:
            from ai_agent import LinkedInDataExtractor
            ai_agent_instance = LinkedInDataExtractor(openai_api_key=openai_api_key)
        else:
            ai_agent_instance = ai_agent
        
        # Process the file with chosen method
        logger.info(f"Processing uploaded file: {temp_path} with {parsing_method} parsing")
        results = ai_agent_instance.process_mhtml_file(temp_path, use_ai=(parsing_method == 'ai'))
        
        if results.get("success"):
            # Store results in session for display
            session_data = {
                'filename': filename,
                'results': results,
                'timestamp': timestamp
            }
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
            
            flash('File processed successfully!', 'success')
            # Store results in session and redirect to results page
            session['upload_data'] = session_data
            return redirect(url_for('results'))
        else:
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
            
            flash(f'Error processing file: {results.get("error", "Unknown error")}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error in upload_file: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display results page."""
    upload_data = session.get('upload_data')
    if not upload_data:
        flash('No results found. Please upload a file first.', 'error')
        return redirect(url_for('index'))
    return render_template('results.html', data=upload_data)

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for processing files (for AJAX calls)."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        # Process the file
        results = ai_agent.process_mhtml_file(temp_path)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in api_process: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/csv')
def export_csv():
    """Export data as CSV."""
    try:
        # Get data from request parameters
        data_json = request.args.get('data')
        if not data_json:
            flash('No data to export', 'error')
            return redirect(url_for('index'))
        
        data = json.loads(data_json)
        extracted_data = data.get('extracted_data', [])
        
        if not extracted_data:
            flash('No data to export', 'error')
            return redirect(url_for('index'))
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}.csv"
        filepath = ai_agent.export_to_csv(extracted_data, filename)
        
        # Send file to user
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error in export_csv: {e}")
        flash(f'Error exporting CSV: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export/json')
def export_json():
    """Export data as JSON."""
    try:
        # Get data from request parameters
        data_json = request.args.get('data')
        if not data_json:
            flash('No data to export', 'error')
            return redirect(url_for('index'))
        
        data = json.loads(data_json)
        extracted_data = data.get('extracted_data', [])
        
        if not extracted_data:
            flash('No data to export', 'error')
            return redirect(url_for('index'))
        
        # Export to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}.json"
        filepath = ai_agent.export_to_json(extracted_data, filename)
        
        # Send file to user
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error in export_json: {e}")
        flash(f'Error exporting JSON: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 