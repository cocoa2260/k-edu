scores = [0.42, 0.91, 0.77, 0.95]
percentages = [round(score * 100) for score in scores]
high_scores = [score for score in scores if score >= 0.8]

print(percentages)
print(high_scores)
