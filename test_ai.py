from ai_service import calculate_similarity

text1 = "Need desktop computers for office"
text2 = "Procurement of desktop PCs"

score = calculate_similarity(text1, text2)

print("Similarity Score:", score)