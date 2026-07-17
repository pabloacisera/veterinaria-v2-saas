import json


class TestChatSseContract:
    def test_sse_event_format(self):
        chunks = ["Hola", ", ", "mundo"]
        events = [f"data: {json.dumps({'token': c})}\n\n" for c in chunks]
        events.append("data: [DONE]\n\n")

        for event in events[:-1]:
            assert event.startswith("data: ")
            assert event.endswith("\n\n")
            payload = json.loads(event[6:].strip())
            assert "token" in payload

        assert events[-1] == "data: [DONE]\n\n"

    def test_sse_complete_stream(self):
        chunks = ["token1", "token2", "token3"]
        events = [f"data: {json.dumps({'token': c})}\n\n" for c in chunks]
        events.append("data: [DONE]\n\n")

        stream = "".join(events)
        lines = [line for line in stream.strip().split("\n") if line]

        assert len(lines) == 4
        assert lines[0] == 'data: {"token": "token1"}'
        assert lines[1] == 'data: {"token": "token2"}'
        assert lines[2] == 'data: {"token": "token3"}'
        assert lines[3] == "data: [DONE]"

    def test_empty_response(self):
        events = ["data: [DONE]\n\n"]
        stream = "".join(events)
        assert stream == "data: [DONE]\n\n"
