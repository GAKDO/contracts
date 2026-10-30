# 이벤트

RabbitMQ `trace.events`로 오가는 이벤트 5종의 JSON Schema를 둔다. 봉투(schemaVersion·eventId·occurredAt·rentalId·checkpointId)는
GAKDO/docs `design/mvp-design.md`의 "이벤트 계약"을 따른다.
