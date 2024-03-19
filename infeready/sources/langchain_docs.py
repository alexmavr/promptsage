from .. import Source, UnauthorizedError

class LangchainDocuments(Source):
    def __init__(self, documents):
        self.documents = documents

    def content(self, user_id: None) -> str:
        res = []
        for doc in self.documents:
            if user_id and "user_id" in doc.metadata and user_id  != doc.metadata["user_id"]:
                raise UnauthorizedError()
            res.append(doc.page_content)
        return " ".join(res)
