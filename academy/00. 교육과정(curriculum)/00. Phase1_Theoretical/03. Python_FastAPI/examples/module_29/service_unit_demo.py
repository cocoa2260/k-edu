class SummaryService:
    def summarize(self, text: str, max_words: int = 3) -> str:
        normalized = text.strip()
        if not normalized:
            raise ValueError("text is required")
        return " ".join(normalized.split()[:max_words])

service = SummaryService()
assert service.summarize("one two three four") == "one two three"
print("service test passed")
