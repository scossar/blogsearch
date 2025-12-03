import chromadb
import uuid
from chromadb.utils import embedding_functions

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)
# client = chromadb.PersistentClient("./tutorial_data")
# with Chroma server running
client = chromadb.HttpClient(host="localhost", port=8000)

collection = client.get_or_create_collection(
    name="policies",
    embedding_function=sentence_transformer_ef,  # type: ignore (the ignore type directive is used in the Chroma code too)
)
# collection = client.create_collection(name="policies")

with open("policies.txt", "r", encoding="utf-8") as f:
    policies: list[str] = f.read().splitlines()

# add the policies to the collection with the `collection.add` method
# each record in the collection needs a unique id
# Note: this only needs to be run once
collection.add(
    ids=[str(uuid.uuid4()) for _ in policies],
    documents=policies,
    metadatas=[{"line": line} for line in range(len(policies))],
)

records = collection.peek(1)
print("records type", type(records))
# records type <class 'dict'>
print("embeddings type", type(records["embeddings"]))
# embeddings type <class 'numpy.ndarray'>
print("embeddings shape", records["embeddings"].shape)
# embeddings shape (1, 384)
print("embeddings[0][:10]", records["embeddings"][0][:10])
# embeddings[0][:10] [-0.00417381 -0.02453116  0.0873247   0.00715757  0.06604723  0.02518193
#  -0.11666935 -0.03335944 -0.02328851  0.11421866]

# query the collection
results = collection.query(
    query_texts=["Do you accept returns?", "Can I get my item gift wrapped?"],
    n_results=5,  # by default Chroma will return 10 results
)

for i, query_results in enumerate(results["documents"]):
    print(f"\nQuery {i}")
    print("\n".join(query_results))
