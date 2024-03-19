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
    metadata=[{"user_id": f"user{i}"} for i in range(len(texts))]  # Each text is owned by a different user
)

# The following are defined in the application's context
query = "What do I know as a user?"
user_id = "user1"

docs = db.similarity_search(query)
prompt = messages_prompt(
   [{"role": "user", "message": query}],
   sources=[LangchainDocuments(docs)],
   user_id=user_id,
   access_control_policy=AccessControlPolicy.skip_unauthorized,
)

chain = prompt.to_langchain_messages() | ChatOpenAI()
print(chain.invoke())