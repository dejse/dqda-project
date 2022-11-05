from pathlib import Path
from datetime import date

data_path = Path("./data")
now = date.today().strftime("%Y-%m-%d")

for f in data_path.iterdir():
  name = f.name.replace(" - ", "_")
  f.rename(Path(data_path, name))

