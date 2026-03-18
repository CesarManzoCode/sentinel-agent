# Local setup

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
sentinel config validate
pytest
```

For richer semantic memory, also install the optional memory extra:

```bash
pip install -e ".[dev,memory]"
```
