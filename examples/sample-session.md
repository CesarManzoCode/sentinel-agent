# Sample session

```text
$ sentinel chat
sentinel> inspect why my python app in ~/work/demo is crashing on startup

[planning] deriving capability scope
[tool] filesystem.navigator.list_dir ~/work/demo
[tool] filesystem.reader.read_file ~/work/demo/pyproject.toml
[tool] terminal.run ["python", "-m", "pytest", "-q"] cwd=~/work/demo
[reflecting] detected failing import path
assistant> The crash is caused by an import path mismatch in `src/demo/__init__.py`...
```
