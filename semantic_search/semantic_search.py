from sentence_transformers import SentenceTransformer


class SemanticSearch:
    def __init__(self, model_name: str = "all-mpnet-base-v2", persist_dir: str = "./"):
        self.model = SentenceTransformer(model_name)
