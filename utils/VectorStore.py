import chromadb
from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import SentenceTransformerEmbeddingFunction

from pathlib import Path

class VectorStore:
    def __init__(self , feeder_id):
        curr_dir = Path(__file__).resolve().parent

        chromadb_path = curr_dir.parent / "chromadb/"

        self.client = chromadb.PersistentClient(path= str(chromadb_path))

        self.embedding_fn = SentenceTransformerEmbeddingFunction(model_name= "all-MiniLM-L6-v2")

        self.collection = self.client.get_or_create_collection(
            name = feeder_id,
            embedding_function= self.embedding_fn
        )

    def upsert_batch(self , ids , documents , metadatas):
        self.collection.upsert( 
            ids = ids,
            documents= documents, 
            metadatas=metadatas)
        

    def query(self , question, n_result = 5 ):
        result = self.collection.query(
            query_texts=[question],
            n_results= n_result
        )

        ids = result['ids'][0]
        documents = result['documents'][0]
        distances = result['distances'][0]
        metadatas = result["metadatas"][0]

        return list(zip(ids, documents , distances , metadatas))
    

    def filter(self , conditions : list  ,logic : str = "$and" , ):
        result = self.collection.get( where= {logic : conditions})
        return result