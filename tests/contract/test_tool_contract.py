from datetime import datetime, timezone
from pathlib import Path

import pytest

from sentinel.domain.common.ids import InvocationId, SessionId
from sentinel.domain.tools.entities import ToolInvocation
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy
from sentinel.infrastructure.tools.filesystem.reader import FilesystemReaderTool


@pytest.mark.asyncio
async def test_filesystem_reader_tool_contract(tmp_path: Path) -> None:
    target = tmp_path / "demo.txt"
    target.write_text("hello world", encoding="utf-8")
    tool = FilesystemReaderTool.create(PathPolicy([tmp_path.resolve()]))

    invocation = ToolInvocation(
        invocation_id=InvocationId.new(),
        session_id=SessionId.new(),
        tool_name=tool.spec.name,
        arguments={"path": str(target)},
        requested_at=datetime.now(timezone.utc),
    )
    result = await tool.execute(invocation)

    assert result.success is True
    assert result.tool_name == "filesystem.reader"
    assert "hello world" in result.stdout
