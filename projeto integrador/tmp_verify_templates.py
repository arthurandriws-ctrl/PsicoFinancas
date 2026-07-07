from pathlib import Path
from jinja2 import Environment, FileSystemLoader

root = Path(r'd:\projeto integrador\templates')
env = Environment(loader=FileSystemLoader(str(root)))
files = [name for name in env.list_templates() if name.endswith('.html')]
for name in files:
    env.get_template(name)
print(f'templates_compilados={len(files)}')
