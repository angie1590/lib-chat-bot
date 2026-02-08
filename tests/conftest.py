import sys
from pathlib import Path

# Agregar src/ al path para que los tests puedan importar lib_chat_bot
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
