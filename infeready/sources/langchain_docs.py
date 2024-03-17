from .. import Source

class LangchainDocuments(Source):
    def __init__(self, documents):
        self.documents = documents

    def content(self) -> str:
        return " ".join([doc.page_content for doc in self.documents])
