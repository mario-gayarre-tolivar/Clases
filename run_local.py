import os
import subprocess
import sys
import time
import signal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
FRONTEND_DIR = ROOT / "frontend"

if not PYTHON.exists():
    PYTHON = Path(sys.executable)

def main():
    backend_env = os.environ.copy()
    backend_src = str(ROOT / "backend" / "src")
    backend_env["PYTHONPATH"] = (
        f"{backend_src};{backend_env.get('PYTHONPATH', '')}"
        if os.name == "nt"
        else f"{backend_src}:{backend_env.get('PYTHONPATH', '')}"
    )
    backend_env["TUTORING_DB_PATH"] = str(ROOT / "tutoring.sqlite3")

    print("=" * 60)
    print(" Arrancando aplicacion pedagogica local")
    print(" - Backend:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)")
    print(" - Frontend: http://localhost:5173")
    print(" Presiona Ctrl+C para detener ambos servidores limpiamente")
    print("=" * 60)

    backend_proc = subprocess.Popen(
        [
            str(PYTHON),
            "-m",
            "uvicorn",
            "tutoring.presentation.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ],
        cwd=str(ROOT),
        env=backend_env,
    )

    frontend_cmd = "npm.cmd run dev" if os.name == "nt" else "npm run dev"
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=str(FRONTEND_DIR),
        shell=True,
    )

    def shutdown(signum=None, frame=None):
        print("\nDeteniendo servidores...")
        for proc in (frontend_proc, backend_proc):
            if proc.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        f"taskkill /F /T /PID {proc.pid}",
                        shell=True,
                        capture_output=True,
                    )
                else:
                    proc.terminate()
        print("Servidores detenidos.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            if backend_proc.poll() is not None:
                print("Backend finalizado inesperadamente.")
                shutdown()
            if frontend_proc.poll() is not None:
                print("Frontend finalizado inesperadamente.")
                shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
