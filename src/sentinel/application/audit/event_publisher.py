from __future__ import annotations

from dataclasses import dataclass, field

from sentinel.domain.audit.entities import AuditEvent
from sentinel.domain.audit.ports import EventPublisherPort


@dataclass(slots=True)
class EventPublisher(EventPublisherPort):
    published: list[AuditEvent] = field(default_factory=list)

    def publish(self, event: AuditEvent) -> None:
        self.published.append(event)
