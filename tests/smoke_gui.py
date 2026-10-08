import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("smoke_r1_r2_gui.py")),run_name="__main__")
