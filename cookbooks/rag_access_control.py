# %pip install --upgrade --quiet  langchain langchain-openai faiss-cpu tiktoken

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from infeready import messages_prompt, AccessControlPolicy
from infeready.sources import LangchainDocuments

texts = [
    "User 1 knows that the password is XXX", 
    "User 2 knows that the password is YYY", 
    "User 3 knows that the password is ZZZ", 
]

db = FAISS.from_texts(
    texts,
    embedding=OpenAIEmbeddings(),
    metadatas=[{"user_id": f"user{i}"} for i in range(1, len(texts)+1)]  # Each text is owned by a different user
)

# The following are defined in the application's context
query = "What do I know as a user?"
user_id = "user2"

docs = db.similarity_search(query)
print(docs)

prompt = messages_prompt(
   [{"role": "user", "content": query}],
   sources=[LangchainDocuments(docs)],
   user_id=user_id,
   access_control_policy=AccessControlPolicy.skip_unauthorized,
)

print(ChatOpenAI().invoke(prompt.to_langchain_messages()))

# Returns: As a user, you know your password is "YYY"