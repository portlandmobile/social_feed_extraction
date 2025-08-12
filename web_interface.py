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
# Use default Flask session handling (in-memory) for better compatibility

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mhtml', 'mht'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Temporary file cleanup
def cleanup_temp_file(filepath):
    """Clean up temporary file after sending."""
    try:
        if os.path.exists(filepath):
            os.unlink(filepath)
            logger.info(f"Cleaned up temporary file: {filepath}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {filepath}: {e}")

# Initialize the AI agent (will be recreated for each request)
def create_ai_agent(openai_api_key=None, gemini_api_key=None, ai_model="chatgpt"):
    """Create a fresh AI agent instance for each request."""
    from ai_agent import LinkedInDataExtractor
    return LinkedInDataExtractor(
        openai_api_key=openai_api_key, 
        gemini_api_key=gemini_api_key,
        ai_model=ai_model
    )

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with file upload form."""
    # Clear any existing session data to ensure clean state
    if 'upload_data' in session:
        del session['upload_data']
        logger.info("Cleared existing session data")
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
        
        # Get parsing method and API keys
        parsing_method = request.form.get('parsing_method', 'traditional')
        openai_api_key = request.form.get('openai_api_key', '')
        gemini_api_key = request.form.get('gemini_api_key', '')
        ai_model = request.form.get('ai_model', 'chatgpt')
        
        # Create a fresh AI agent instance for each request
        ai_agent_instance = create_ai_agent(
            openai_api_key=openai_api_key if parsing_method == 'ai' and ai_model == 'chatgpt' else None,
            gemini_api_key=gemini_api_key if parsing_method == 'ai' and ai_model == 'gemini' else None,
            ai_model=ai_model if parsing_method == 'ai' else 'chatgpt'
        )
        
        # Process the file with chosen method
        logger.info(f"Processing uploaded file: {temp_path} with {parsing_method} parsing using {ai_model}")
        logger.info(f"File size: {os.path.getsize(temp_path)} bytes")
        results = ai_agent_instance.process_mhtml_file(temp_path, use_ai=(parsing_method == 'ai'), ai_model=ai_model)
        #logger.info(f"Processing complete. Results: {results}")
        logger.info(f"Results success: {results.get('success')}")
        logger.info(f"Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        logger.info(f"Data count: {len(results.get('extracted_data', [])) if isinstance(results, dict) else 'No extracted_data'}")
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        if results.get("success"):
            # Check if the data is too large for session storage
            extracted_data_count = len(results.get('extracted_data', []))
            logger.info(f"Preparing to store session data. Results keys: {list(results.keys())}")
            logger.info(f"Extracted data count: {extracted_data_count}")
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
            
            flash('File processed successfully!', 'success')
            
            # Check if data is too large for session cookies or if AI enhancement was used
            # Use database storage for AI-enhanced data or datasets over 20 records
            if extracted_data_count > 20 or parsing_method == 'ai':
                logger.info(f"Using database storage approach: {extracted_data_count} records, AI enhancement: {parsing_method == 'ai'}")
                
                # Store results in database instead of session
                from database import get_database
                db = get_database()
                
                try:
                    # Store results in database
                    result_id = db.store_results(
                        filename=filename,
                        timestamp=timestamp,
                        data_count=extracted_data_count,
                        processing_method='database',
                        results=results
                    )
                    
                    logger.info(f"Results stored in database with ID: {result_id}")
                    
                    # If AI enhancement was used, store enhanced data in separate table
                    if parsing_method == 'ai' and results.get('extracted_data'):
                        enhanced_data = results.get('extracted_data')
                        logger.info(f"AI enhancement detected. Checking for enhanced data...")
                        logger.info(f"Enhanced data type: {type(enhanced_data)}")
                        logger.info(f"Enhanced data length: {len(enhanced_data) if enhanced_data else 'None'}")
                        
                        if enhanced_data and len(enhanced_data) > 0:
                            first_record = enhanced_data[0]
                            logger.info(f"First record keys: {list(first_record.keys()) if isinstance(first_record, dict) else 'Not a dict'}")
                            
                            # Check if this is enhanced data (has Company and Location fields)
                            if isinstance(first_record, dict) and 'Company' in first_record and 'Location' in first_record:
                                logger.info("Enhanced data detected with Company and Location fields")
                                logger.info(f"Sample Company: {first_record.get('Company', 'N/A')}")
                                logger.info(f"Sample Location: {first_record.get('Location', 'N/A')}")
                                
                                if db.store_enhanced_data(result_id, enhanced_data):
                                    logger.info(f"Enhanced data stored successfully in database with {len(enhanced_data)} records")
                                    logger.info(f"Enhanced data sample: Company='{first_record.get('Company', 'N/A')}', Location='{first_record.get('Location', 'N/A')}'")
                                else:
                                    logger.warning("Failed to store enhanced data in database")
                            else:
                                logger.info("No Company/Location fields detected in enhanced data")
                                logger.info(f"Available fields: {list(first_record.keys()) if isinstance(first_record, dict) else 'Not a dict'}")
                        else:
                            logger.info("No enhanced data available for storage")
                    else:
                        logger.info(f"AI enhancement not used (parsing_method: {parsing_method})")
                    
                    # Store only minimal metadata in session
                    session['upload_data'] = {
                        'filename': filename,
                        'timestamp': timestamp,
                        'data_count': extracted_data_count,
                        'processing_method': 'database',
                        'result_id': result_id
                    }
                    
                    logger.info(f"Session metadata stored: filename={filename}, result_id={result_id}, processing_method=database")
                    
                    # Return JSON response that JavaScript can handle
                    return jsonify({
                        'success': True,
                        'message': f'Successfully processed {extracted_data_count} records',
                        'redirect_url': '/results',
                        'data_count': extracted_data_count,
                        'filename': filename
                    })
                    
                except Exception as db_error:
                    logger.error(f"Error storing results in database: {db_error}")
                    # Fallback to session storage for small datasets
                    logger.info("Falling back to session storage due to database error")
                    session_data = {
                        'filename': filename,
                        'results': results,
                        'timestamp': timestamp
                    }
                    session['upload_data'] = session_data
                    return redirect(url_for('results'))
            else:
                # For smaller datasets, try session storage
                session_data = {
                    'filename': filename,
                    'results': results,
                    'timestamp': timestamp
                }
                
                try:
                    session['upload_data'] = session_data
                    logger.info(f"Session data stored successfully. Session keys: {list(session.keys())}")
                    return redirect(url_for('results'))
                except Exception as session_error:
                    logger.error(f"Error storing session data: {session_error}")
                    # Fallback: render results directly instead of redirecting
                    logger.info("Falling back to direct rendering due to session storage failure")
                    return render_template('results.html', data=session_data)
        else:
            logger.warning(f"File processing failed. Results: {results}")
            logger.warning(f"Error message: {results.get('error', 'Unknown error')}")
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
            
            flash(f'Error processing file: {results.get("error", "Unknown error")}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error in upload_file: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display results page."""
    logger.info(f"Results route accessed. Session keys: {list(session.keys())}")
    upload_data = session.get('upload_data')
    logger.info(f"Results route accessed. Session data: {upload_data is not None}")
    
    if upload_data:
        logger.info(f"Results data: filename={upload_data.get('filename')}, data_count={upload_data.get('data_count', 'Unknown')}")
        logger.info(f"Results data keys: {list(upload_data.keys())}")
        logger.info(f"Processing method: {upload_data.get('processing_method')}")
        
        # Check if this was a database storage
        if upload_data.get('processing_method') == 'database':
            logger.info("Database storage detected in results route")
            result_id = upload_data.get('result_id')
            
            if result_id:
                try:
                    # Retrieve results from database
                    from database import get_database
                    db = get_database()
                    
                    results = db.retrieve_results(
                        filename=upload_data.get('filename'),
                        timestamp=upload_data.get('timestamp')
                    )
                    
                    if results:
                        logger.info(f"Results retrieved successfully from database")
                        
                        # Check if enhanced data exists and use it instead of raw results
                        enhanced_data = db.get_enhanced_data(result_id)
                        if enhanced_data:
                            logger.info(f"Enhanced data found with {len(enhanced_data)} records")
                            # Replace the extracted_data with enhanced data
                            results['extracted_data'] = enhanced_data
                            # Update the data count
                            results['summary']['total_posts'] = len(enhanced_data)
                        else:
                            logger.info("No enhanced data found, using original extracted data")
                        
                        # Render results template
                        return render_template('results.html', data={
                            'filename': upload_data.get('filename'),
                            'results': results,
                            'timestamp': upload_data.get('timestamp')
                        })
                    else:
                        logger.error("No results found in database")
                        flash('Results not found in database. Please try uploading the file again.', 'error')
                        return redirect(url_for('index'))
                        
                except Exception as db_error:
                    logger.error(f"Error retrieving results from database: {db_error}")
                    flash('Error retrieving results from database. Please try uploading the file again.', 'error')
                    return redirect(url_for('index'))
            else:
                logger.error("No result ID specified in session data")
                flash('Results data not found. Please try uploading the file again.', 'error')
                return redirect(url_for('index'))
    else:
        logger.warning("No upload_data found in session")
    
    if not upload_data:
        flash('No results found. Please upload a file first.', 'error')
        logger.warning("Redirecting to index due to missing session data")
        return redirect(url_for('index'))
    
    logger.info("Rendering results template successfully")
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
        
        # Get API keys and model from request
        openai_api_key = request.form.get('openai_api_key', '')
        gemini_api_key = request.form.get('gemini_api_key', '')
        ai_model = request.form.get('ai_model', 'chatgpt')
        use_ai = request.form.get('use_ai', 'false').lower() == 'true'
        
        # Process the file with a fresh AI agent instance
        ai_agent_instance = create_ai_agent(
            openai_api_key=openai_api_key if use_ai and ai_model == 'chatgpt' else None,
            gemini_api_key=gemini_api_key if use_ai and ai_model == 'gemini' else None,
            ai_model=ai_model if use_ai else 'chatgpt'
        )
        results = ai_agent_instance.process_mhtml_file(temp_path, use_ai=use_ai, ai_model=ai_model)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in api_process: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/csv', methods=['POST'])
def export_csv():
    """Export data as CSV."""
    try:
        # Get data from POST request
        data_json = request.form.get('data')
        if not data_json:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        data = json.loads(data_json)
        extracted_data = data.get('extracted_data', [])
        
        if not extracted_data:
            return jsonify({'success': False, 'error': 'No data to export'}), 400
        
        # Create CSV content
        import pandas as pd
        
        # Ensure all required columns exist
        columns = ['Name', 'Title', 'Period', 'Details', 'Company', 'Location']
        
        df = pd.DataFrame(extracted_data)
        
        # Add missing columns if they don't exist
        for col in columns:
            if col not in df.columns:
                df[col] = 'N/A'
        
        # Reorder columns to ensure consistent output
        df = df[columns]
        
        # Create CSV content
        csv_content = df.to_csv(index=False)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}.csv"
        
        # Create temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(csv_content)
        temp_file.close()
        
        # Send file to user
        response = send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
        # Clean up temporary file after response is sent
        @response.call_on_close
        def cleanup():
            cleanup_temp_file(temp_file.name)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_csv: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/csv-session', methods=['GET'])
def export_csv_session():
    """Export data as CSV using session data (for large datasets)."""
    try:
        # Get data from session
        if 'upload_data' not in session:
            flash('No data available for export', 'error')
            return redirect(url_for('index'))
        
        upload_data = session['upload_data']
        
        # If data is stored in database, retrieve it
        if upload_data.get('processing_method') == 'database':
            from database import get_database
            db = get_database()
            results = db.retrieve_results(upload_data['filename'], upload_data['timestamp'])
            if results:
                # Check if enhanced data exists and use it instead
                result_id = upload_data.get('result_id')
                if result_id:
                    enhanced_data = db.get_enhanced_data(result_id)
                    if enhanced_data:
                        logger.info(f"Using enhanced data with {len(enhanced_data)} records for CSV export")
                        extracted_data = enhanced_data
                    else:
                        logger.info("No enhanced data found, using original extracted data")
                        extracted_data = results.get('extracted_data', [])
                else:
                    extracted_data = results.get('extracted_data', [])
            else:
                flash('Data not found in database', 'error')
                return redirect(url_for('index'))
        else:
            # Get data from session
            results = session.get('upload_data', {}).get('results', {})
            extracted_data = results.get('extracted_data', [])
        
        if not extracted_data:
            flash('No data to export', 'error')
            return redirect(url_for('index'))
        
        # Create CSV content
        import pandas as pd
        
        # Ensure all required columns exist
        columns = ['Name', 'Title', 'Period', 'Details', 'Company', 'Location']
        
        df = pd.DataFrame(extracted_data)
        
        # Add missing columns if they don't exist
        for col in columns:
            if col not in df.columns:
                df[col] = 'N/A'
        
        # Reorder columns to ensure consistent output
        df = df[columns]
        
        # Create CSV content
        csv_content = df.to_csv(index=False)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}.csv"
        
        # Create temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(csv_content)
        temp_file.close()
        
        # Send file to user
        response = send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
        # Clean up temporary file after response is sent
        @response.call_on_close
        def cleanup():
            cleanup_temp_file(temp_file.name)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_csv_session: {e}")
        flash(f'Error exporting CSV: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export/json', methods=['POST'])
def export_json():
    """Export data as JSON."""
    try:
        # Get data from POST request
        data_json = request.form.get('data')
        if not data_json:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        data = json.loads(data_json)
        extracted_data = data.get('extracted_data', [])
        
        if not extracted_data:
            return jsonify({'success': False, 'error': 'No data to export'}), 400
        
        # Create JSON content
        json_content = json.dumps(extracted_data, indent=2, ensure_ascii=False)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}.json"
        
        # Create temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write(json_content)
        temp_file.close()
        
        # Send file to user
        response = send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
        # Clean up temporary file after response is sent
        @response.call_on_close
        def cleanup():
            cleanup_temp_file(temp_file.name)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_json: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/json-session', methods=['GET'])
def export_json_session():
    """Export data as JSON using session data (for large datasets)."""
    try:
        # Get data from session
        if 'upload_data' not in session:
            flash('No data available for export', 'error')
            return redirect(url_for('index'))
        
        upload_data = session['upload_data']
        
        # If data is stored in database, retrieve it
        if upload_data.get('processing_method') == 'database':
            from database import get_database
            db = get_database()
            results = db.retrieve_results(upload_data['filename'], upload_data['timestamp'])
            if results:
                # Check if enhanced data exists and use it instead
                result_id = upload_data.get('result_id')
                if result_id:
                    enhanced_data = db.get_enhanced_data(result_id)
                    if enhanced_data:
                        logger.info(f"Using enhanced data with {len(enhanced_data)} records for JSON export")
                        extracted_data = enhanced_data
                    else:
                        logger.info("No enhanced data found, using original extracted data")
                        extracted_data = results.get('extracted_data', [])
                else:
                    extracted_data = results.get('extracted_data', [])
            else:
                flash('Data not found in database', 'error')
                return redirect(url_for('index'))
        else:
            # Get data from session
            results = session.get('upload_data', {}).get('results', {})
            extracted_data = results.get('extracted_data', [])
        
        if not extracted_data:
            flash('No data available for export', 'error')
            return redirect(url_for('index'))
        
        # Create JSON content
        json_content = json.dumps(extracted_data, indent=2, ensure_ascii=False)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}.json"
        
        # Create temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write(json_content)
        temp_file.close()
        
        # Send file to user
        response = send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
        # Clean up temporary file after response is sent
        @response.call_on_close
        def cleanup():
            cleanup_temp_file(temp_file.name)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_json_session: {e}")
        flash(f'Error exporting JSON: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/debug/session')
def debug_session():
    """Debug endpoint to check session data."""
    session_data = dict(session)
    return jsonify({
        'session_keys': list(session_data.keys()),
        'upload_data_exists': 'upload_data' in session_data,
        'upload_data': session_data.get('upload_data', 'Not found'),
        'session_size': len(str(session_data))
    })

@app.route('/debug/test-session')
def test_session():
    """Test endpoint to verify session functionality."""
    test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
    session['test_data'] = test_data
    return jsonify({
        'message': 'Test data stored in session',
        'stored_data': session.get('test_data'),
        'all_session_keys': list(session.keys())
    })

@app.route('/debug/test-ai-agent')
def test_ai_agent():
    """Test endpoint to verify AI agent functionality."""
    try:
        # Create a test AI agent instance
        ai_agent_instance = create_ai_agent()
        logger.info("AI agent created successfully")
        
        # Test with a simple string to see if basic functionality works
        test_html = "<div class='feed-shared-update-v2'><span aria-hidden='true'>Test User</span></div>"
        results = ai_agent_instance.extract_linkedin_data(test_html)
        
        return jsonify({
            'message': 'AI agent test successful',
            'test_results': results,
            'agent_type': str(type(ai_agent_instance))
        })
    except Exception as e:
        logger.error(f"AI agent test failed: {e}")
        import traceback
        return jsonify({
            'message': 'AI agent test failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/debug/database')
def debug_database():
    """Debug endpoint to check database status and contents."""
    try:
        from database import get_database
        db = get_database()
        
        # Get database summary
        summary = db.get_results_summary()
        
        # Clean up expired results
        db.cleanup_expired_results()
        
        return jsonify({
            'database_status': 'healthy',
            'total_results': len(summary),
            'recent_results': summary[:10],  # Show last 10 results
            'database_path': db.db_path
        })
    except Exception as e:
        logger.error(f"Database debug failed: {e}")
        import traceback
        return jsonify({
            'database_status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/debug/step-by-step/<filename>')
def debug_step_by_step(filename):
    """Debug endpoint to test file processing step by step."""
    try:
        # Find the file in uploads directory
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': f'File {filename} not found in uploads directory'})
        
        logger.info(f"Starting step-by-step debug for file: {file_path}")
        
        # Step 1: Test file reading
        ai_agent_instance = create_ai_agent()
        try:
            mhtml_message = ai_agent_instance.read_mhtml_file(file_path)
            step1_success = True
            step1_info = "MHTML file read successfully"
        except Exception as e:
            step1_success = False
            step1_info = f"Failed to read MHTML: {str(e)}"
        
        # Step 2: Test HTML extraction
        if step1_success:
            try:
                html_content = ai_agent_instance.extract_html_content(mhtml_message)
                step2_success = bool(html_content)
                step2_info = f"HTML extracted: {len(html_content)} characters" if html_content else "No HTML content found"
            except Exception as e:
                step2_success = False
                step2_info = f"Failed to extract HTML: {str(e)}"
        else:
            step2_success = False
            step2_info = "Skipped due to step 1 failure"
        
        # Step 3: Test data extraction
        if step2_success:
            try:
                extracted_data = ai_agent_instance.extract_linkedin_data(html_content)
                step3_success = True
                step3_info = f"Data extracted: {len(extracted_data)} records"
            except Exception as e:
                step3_success = False
                step3_info = f"Failed to extract data: {str(e)}"
        else:
            step3_success = False
            step3_info = "Skipped due to step 2 failure"
        
        return jsonify({
            'filename': filename,
            'file_size': os.path.getsize(file_path),
            'step1_file_reading': {'success': step1_success, 'info': step1_info},
            'step2_html_extraction': {'success': step2_success, 'info': step2_info},
            'step3_data_extraction': {'success': step3_success, 'info': step3_info},
            'overall_success': all([step1_success, step2_success, step3_success])
        })
        
    except Exception as e:
        logger.error(f"Step-by-step debug failed: {e}")
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 