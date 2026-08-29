from flask import Flask, render_template_string, jsonify
import subprocess
import os
import signal
import psutil

app = Flask(__name__)

# Archivo donde guardaremos el PID del proceso
PID_FILE = "bot.pid"

# HTML de la interfaz
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Control del Bot de Telegram</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
            background: #f0f0f0;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status {
            font-size: 20px;
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
        }
        .status.active {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.inactive {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .btn {
            padding: 12px 30px;
            font-size: 18px;
            margin: 10px 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: scale(1.05);
        }
        .btn-start {
            background: #28a745;
            color: white;
        }
        .btn-start:hover {
            background: #218838;
        }
        .btn-stop {
            background: #dc3545;
            color: white;
        }
        .btn-stop:hover {
            background: #c82333;
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        #message {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
        }
        .success {
            background: #d4edda;
            color: #155724;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Control del Bot Clonador</h1>
        
        <div id="status-container">
            <div class="status" id="status">Cargando estado...</div>
        </div>

        <div>
            <button class="btn btn-start" id="startBtn" onclick="startBot()">▶ Iniciar Bot</button>
            <button class="btn btn-stop" id="stopBtn" onclick="stopBot()">⏹ Detener Bot</button>
        </div>

        <div id="message"></div>
    </div>

    <script>
        // Función para obtener el estado del bot
        function getStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    const startBtn = document.getElementById('startBtn');
                    const stopBtn = document.getElementById('stopBtn');
                    
                    if (data.status === 'running') {
                        statusDiv.textContent = '✅ Bot activo';
                        statusDiv.className = 'status active';
                        startBtn.disabled = true;
                        stopBtn.disabled = false;
                    } else {
                        statusDiv.textContent = '❌ Bot detenido';
                        statusDiv.className = 'status inactive';
                        startBtn.disabled = false;
                        stopBtn.disabled = true;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        // Función para iniciar el bot
        function startBot() {
            fetch('/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    const msg = document.getElementById('message');
                    if (data.success) {
                        msg.textContent = '✅ Bot iniciado correctamente';
                        msg.className = 'success';
                        getStatus();
                    } else {
                        msg.textContent = '❌ Error: ' + data.message;
                        msg.className = 'error';
                    }
                })
                .catch(error => {
                    document.getElementById('message').textContent = '❌ Error al iniciar';
                    document.getElementById('message').className = 'error';
                });
        }

        // Función para detener el bot
        function stopBot() {
            fetch('/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    const msg = document.getElementById('message');
                    if (data.success) {
                        msg.textContent = '⏹ Bot detenido correctamente';
                        msg.className = 'success';
                        getStatus();
                    } else {
                        msg.textContent = '❌ Error: ' + data.message;
                        msg.className = 'error';
                    }
                })
                .catch(error => {
                    document.getElementById('message').textContent = '❌ Error al detener';
                    document.getElementById('message').className = 'error';
                });
        }

        // Obtener estado al cargar la página
        getStatus();

        // Actualizar estado cada 5 segundos
        setInterval(getStatus, 5000);
    </script>
</body>
</html>
"""

def get_pid():
    """Lee el PID guardado"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return None
    return None

def is_process_running(pid):
    """Verifica si un proceso con el PID dado está corriendo"""
    if pid is None:
        return False
    try:
        # Verificar si el proceso existe y es python
        process = psutil.Process(pid)
        return 'python' in process.name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(HTML)

@app.route('/status')
def status():
    """Endpoint para verificar el estado del bot"""
    pid = get_pid()
    is_running = is_process_running(pid)
    return jsonify({
        'status': 'running' if is_running else 'stopped',
        'pid': pid
    })

@app.route('/start', methods=['POST'])
def start_bot():
    """Inicia el bot"""
    # Verificar si ya está corriendo
    pid = get_pid()
    if is_process_running(pid):
        return jsonify({
            'success': False,
            'message': 'El bot ya está corriendo'
        })

    try:
        # Ejecutar el script clonar.py en segundo plano
        process = subprocess.Popen(
            ['python3', 'clonar.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Guardar el PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        return jsonify({
            'success': True,
            'message': 'Bot iniciado correctamente',
            'pid': process.pid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Detiene el bot"""
    pid = get_pid()
    
    if not is_process_running(pid):
        # Limpiar el archivo PID si existe
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return jsonify({
            'success': False,
            'message': 'El bot no estaba corriendo'
        })

    try:
        # Intentar terminar el proceso
        process = psutil.Process(pid)
        process.terminate()  # Enviar SIGTERM
        
        # Esperar unos segundos a que termine
        import time
        time.sleep(2)
        
        # Si aún sigue, forzar
        if process.is_running():
            process.kill()
        
        # Eliminar el archivo PID
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        
        return jsonify({
            'success': True,
            'message': 'Bot detenido correctamente'
        })
    except Exception as e:
        # Si hubo error, limpiar el archivo PID
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return jsonify({
            'success': False,
            'message': f'Error al detener: {str(e)}'
        })

if __name__ == '__main__':
    # Instalar psutil si no está instalado
    try:
        import psutil
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'psutil'])
        import psutil
    
    # Crear la carpeta static si no existe
    os.makedirs('static', exist_ok=True)
    
    # Iniciar el servidor
    app.run(debug=False, host='0.0.0.0', port=5000)