from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text):
    return model.encode(text)

def calculate_similarity(text1, text2):

    emb1 = create_embedding(text1)
    emb2 = create_embedding(text2)

    similarity = cosine_similarity(
        [emb1],
        [emb2]
    )[0][0]

    return float(similarity)