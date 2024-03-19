import pytest
from infeready.infeready  import (
    messages_prompt, 
    EchoSource, 
    NoopFilter, 
    DefaultTemplate, 
    Prompt,
    AccessControlPolicy,
    UnauthorizedError
)

from infeready.sources import LangchainDocuments

def test_echo_source():
    source = EchoSource("source data")
    assert source.content() == "source data"

def test_noop_filter():
    filter = NoopFilter()
    assert filter.filter("test") == "test"

def test_default_template():
    template = DefaultTemplate()
    rendered = template.render("prompt", ["example1", "example2"], ["source1", "source2"])
    assert "prompt" in rendered
    assert "example1" in rendered
    assert "example2" in rendered
    assert "source1" in rendered
    assert "source2" in rendered
    assert "Examples" in rendered
    assert "Sources" in rendered

def test_messages_prompt():
    messages = [{"role": "system", "message": "system prompt"}, {"role": "user", "message": "user prompt"}]
    prompt = messages_prompt(
        messages, 
        examples=["example1", "example2"], 
        sources=[EchoSource("source1"), EchoSource("source2")], 
        filters=[NoopFilter()], 
    )
    assert isinstance(prompt, Prompt)

    str_prompt = prompt.to_str()

    # Test the string output version
    assert "user prompt" in str_prompt
    assert "example1" in str_prompt
    assert "example2" in str_prompt
    assert "source1" in str_prompt
    assert "source2" in str_prompt
    assert "Examples" in str_prompt
    assert "Sources" in str_prompt

def test_langchain_documents():
    from langchain_community.document_loaders.csv_loader import CSVLoader

    loader = CSVLoader(file_path='./tests/test.csv')
    data = loader.load()
    assert len(data) > 0 
    print(data)

    source = LangchainDocuments(data)

    messages = [{"role": "system", "message": "system prompt"}, {"role": "user", "message": "user prompt"}]
    prompt = messages_prompt(
        messages, 
        examples=[], 
        sources=[source], 
    )

    str_prompt = prompt.to_str()
    assert "user prompt" in str_prompt
    assert "testing123" in str_prompt
    assert "testing321" in str_prompt
    assert "values456" in str_prompt
    assert "values654" in str_prompt
    assert "here789" in str_prompt
    assert "there987" in str_prompt

def test_access_control_reject():
    sources = [
    EchoSource("User 1 knows that the password is XXX", "user1"),
    EchoSource("User 2 knows that the password is YYY", "user2"),
    EchoSource("User 3 knows that the password is ZZZ", "user3"),
    ]

    with pytest.raises(UnauthorizedError):
        prompt = messages_prompt(
            [{"role": "user", "message": "What do I know as a user?"}],
            sources=sources,
            user_id="user2",
        )

def test_access_control_skip():
    sources = [
    EchoSource("User 1 knows that the password is XXX", "user1"),
    EchoSource("User 2 knows that the password is YYY", "user2"),
    EchoSource("User 3 knows that the password is ZZZ", "user3"),
    ]

    prompt = messages_prompt(
        [{"role": "user", "message": "What do I know as a user?"}],
        sources=sources,
        user_id="user2",
        access_control_policy=AccessControlPolicy.skip_unauthorized,
    )

    str_prompt = prompt.to_str()
    assert "YYY" in str_prompt
    assert "XXX" not in str_prompt
    assert "ZZZ" not in str_prompt

if __name__ == '__main__':
    pytest.main()