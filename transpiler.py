from pathlib import Path
import wadze

ROOT_DIR = Path(__file__).parent

with open(ROOT_DIR / "input.wasm", "rb") as f:
    module = wadze.parse_module(f.read())

print(module)
