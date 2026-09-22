from types import SimpleNamespace

from invoice_buddy.agent import run_agent


def test_agent_returns_direct_answer(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["model"] == "openai/gpt-oss-20b"
            assert kwargs["tool_choice"] == "auto"
            assert len(kwargs["tools"]) > 0

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="Your total spend is ₹29,500.",
                            tool_calls=None,
                            model_dump=lambda exclude_none=True: {
                                "role": "assistant",
                                "content": ("Your total spend is ₹29,500."),
                            },
                        )
                    )
                ]
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(
        "invoice_buddy.agent.OpenAI",
        FakeOpenAI,
    )

    result = run_agent(
        session=None,
        user_message="What is my total spend?",
    )

    assert result == "Your total spend is ₹29,500."
