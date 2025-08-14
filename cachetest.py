from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Client-side Cache Editor</title></head>
    <body>
      <h2>Edit and Save Data Locally (Client-side)</h2>
      <label for="file1">File 1:</label><br>
      <textarea id="file1" rows="10" cols="50"></textarea><br><br>

      <label for="file2">File 2:</label><br>
      <textarea id="file2" rows="10" cols="50"></textarea><br><br>

      <button onclick="saveData()">Save to LocalStorage</button>

      <script>
        // Load saved data when page loads
        window.onload = () => {
          document.getElementById('file1').value = localStorage.getItem('file1') || '';
          document.getElementById('file2').value = localStorage.getItem('file2') || '';
        };

        // Save textarea content to localStorage
        function saveData() {
          localStorage.setItem('file1', document.getElementById('file1').value);
          localStorage.setItem('file2', document.getElementById('file2').value);
          alert('Data saved locally in your browser!');
        }
      </script>
    </body>
    </html>
    '''
    return render_template_string(html)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
