# Safe tool approval flow

- low risk read-only actions may execute automatically within scope
- medium risk actions show a preview and require explicit `/approve`
- high risk actions always require exact approval and expire quickly

Example preview:

```text
Approval required
tool: filesystem.writer.write_file
risk: HIGH
target: /home/user/work/demo/settings.py
diff:
- DEBUG = True
+ DEBUG = False
token: appr_...
```
