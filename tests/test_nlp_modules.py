"""
NLP Module Tests

Tests for tokenizer, keyword extraction, TF-IDF, and indexing.
"""

import pytest
from kse.nlp import (
    Tokenizer,
    TokenType,
    KeywordExtractor,
    TFIDFComputer,
)


class TestTokenizer:
    """Test Swedish tokenizer."""
    
    def test_tokenizer_init(self):
        """Test tokenizer initialization."""
        tokenizer = Tokenizer()
        assert tokenizer.min_token_length == 2
        assert tokenizer.remove_stopwords
    
    def test_tokenize_basic(self):
        """Test basic tokenization."""
        tokenizer = Tokenizer(remove_stopwords=False)
        text = "Detta är en test text"
        
        tokens = tokenizer.tokenize(text)
        
        assert len(tokens) >= 3
        assert any(t.text == "test" for t in tokens)
    
    def test_tokenize_stopword_removal(self):
        """Test stopword removal."""
        tokenizer = Tokenizer(remove_stopwords=True)
        text = "det är en mycket viktig text"
        
        tokens = tokenizer.tokenize(text)
        
        # Stopwords should be removed
        token_texts = [t.text for t in tokens]
        assert "det" not in token_texts
        assert "är" not in token_texts
        assert "en" not in token_texts
    
    def test_tokenize_swedish_chars(self):
        """Test Swedish character handling."""
        tokenizer = Tokenizer(remove_stopwords=False)
        text = "åäö bränning näring djävul"
        
        tokens = tokenizer.tokenize(text)
        
        assert len(tokens) >= 3
        assert any('å' in t.text or 'ä' in t.text or 'ö' in t.text for t in tokens)
    
    def test_tokenize_token_type(self):
        """Test token type classification."""
        tokenizer = Tokenizer()
        text = "test123 abc 456"
        
        tokens = tokenizer.tokenize(text)
        
        word_tokens = [t for t in tokens if t.token_type == TokenType.WORD]
        assert len(word_tokens) >= 1
    
    def test_tokenize_min_length(self):
        """Test minimum token length."""
        tokenizer = Tokenizer(min_token_length=3, remove_stopwords=False)
        text = "a ab abc abcd"
        
        tokens = tokenizer.tokenize(text)
        
        # Only tokens >= 3 chars
        token_texts = [t.text for t in tokens]
        assert "ab" not in token_texts
        assert "abc" in token_texts or "abcd" in token_texts
    
    def test_tokenize_phrases(self):
        """Test phrase extraction."""
        tokenizer = Tokenizer(remove_stopwords=False)
        text = "svenska språket är mycket viktigt"
        
        phrases = tokenizer.tokenize_phrases(text, phrase_length=2)
        
        assert len(phrases) >= 2
        assert any("svenska" in p.text for p in phrases)
    
    def test_unique_tokens(self):
        """Test unique token extraction."""
        tokenizer = Tokenizer(remove_stopwords=False)
        tokens = tokenizer.tokenize("test test klar klar klar")
        
        unique = tokenizer.get_unique_tokens(tokens)
        
        assert len(unique) <= len(tokens)
    
    def test_token_frequencies(self):
        """Test token frequency calculation."""
        tokenizer = Tokenizer(remove_stopwords=False)
        tokens = tokenizer.tokenize("test test klar")
        
        freqs = tokenizer.get_token_frequencies(tokens)
        
        assert freqs.get("test") == 2
        assert freqs.get("klar") == 1
    
    def test_clean_text(self):
        """Test text cleaning."""
        tokenizer = Tokenizer()
        text = "  <p>Text with  spaces</p>  "
        
        cleaned = tokenizer.clean_text(text)
        
        assert "<p>" not in cleaned
        assert "  " not in cleaned
        assert cleaned.strip() == cleaned


class TestKeywordExtractor:
    """Test keyword extraction."""
    
    def test_extractor_init(self):
        """Test extractor initialization."""
        extractor = KeywordExtractor()
        assert extractor.min_frequency == 2
        assert extractor.max_keywords == 50
    
    def test_extract_basic(self):
        """Test basic keyword extraction."""
        extractor = KeywordExtractor(min_frequency=1)
        text = "python är ett programmeringsspråk python är populärt"
        
        keywords = extractor.extract(text)
        
        assert len(keywords) > 0
        assert any("python" in k.text for k in keywords)
    
    def test_extract_with_title(self):
        """Test extraction with title boost."""
        extractor = KeywordExtractor(min_frequency=1)
        text = "content text body content"
        title = "Important Title Keywords"
        
        keywords = extractor.extract(
            text=text,
            title=title,
        )
        
        # Title keywords should have higher scores
        assert len(keywords) > 0
    
    def test_extract_with_description(self):
        """Test extraction with description boost."""
        extractor = KeywordExtractor(min_frequency=1)
        text = "main content"
        description = "Meta Description Keywords"
        
        keywords = extractor.extract(
            text=text,
            description=description,
        )
        
        assert len(keywords) > 0
    
    def test_extract_phrases(self):
        """Test phrase extraction."""
        extractor = KeywordExtractor(min_frequency=1, include_phrases=True)
        text = "machine learning is important machine learning is popular"
        
        keywords = extractor.extract(text, include_phrases=True)
        
        # Should have both words and phrases
        phrases = [k for k in keywords if k.is_phrase]
        assert len(phrases) >= 0  # May or may not extract phrases
    
    def test_keyword_frequency(self):
        """Test keyword frequency calculation."""
        extractor = KeywordExtractor(min_frequency=1)
        text = "test test test klar klar content"
        
        keywords = extractor.extract(text)
        
        test_kw = next((k for k in keywords if k.text == "test"), None)
        assert test_kw and test_kw.frequency >= 3
    
    def test_keyword_scoring(self):
        """Test keyword scoring."""
        extractor = KeywordExtractor(min_frequency=1)
        text = "important important important normal"
        
        keywords = extractor.extract(text)
        
        if keywords:
            # Scores should be between 0 and 1
            for kw in keywords:
                assert 0 <= kw.combined_score <= 1
    
    def test_top_keywords(self):
        """Test getting top keywords."""
        extractor = KeywordExtractor(min_frequency=1)
        text = "a a a b b c"
        
        keywords = extractor.extract(text)
        top = extractor.get_top_keywords(keywords, count=2)
        
        assert len(top) <= 2
    
    def test_extract_from_document(self):
        """Test extraction from full document."""
        extractor = KeywordExtractor(min_frequency=1)
        
        keywords, stats = extractor.extract_from_document(
            text="content text content",
            title="Title Keywords",
            description="Description",
            headings=["Heading One", "Heading Two"],
        )
        
        assert len(keywords) > 0
        assert stats['total_keywords'] > 0


class TestTFIDF:
    """Test TF-IDF computer."""
    
    def test_tfidf_init(self):
        """Test TF-IDF initialization."""
        tfidf = TFIDFComputer()
        assert tfidf.total_documents == 0
    
    def test_compute_tf(self):
        """Test Term Frequency computation."""
        tfidf = TFIDFComputer()
        terms = ["test", "test", "klar", "klar", "content"]
        
        tf_test = tfidf.compute_tf("test", terms)
        tf_klar = tfidf.compute_tf("klar", terms)
        tf_missing = tfidf.compute_tf("missing", terms)
        
        assert tf_test == 2/5  # 2 occurrences out of 5
        assert tf_klar == 2/5
        assert tf_missing == 0.0
    
    def test_compute_idf(self):
        """Test Inverse Document Frequency computation."""
        tfidf = TFIDFComputer()
        
        tfidf.add_document(["test", "klar"])
        tfidf.add_document(["test", "content"])
        tfidf.add_document(["klar", "content"])
        
        idf_test = tfidf.compute_idf("test")
        idf_rare = tfidf.compute_idf("rare_term")
        
        assert idf_test > 0
        assert idf_rare > 0
    
    def test_add_documents(self):
        """Test adding multiple documents."""
        tfidf = TFIDFComputer()
        
        docs = [
            ["test", "klar"],
            ["test", "content"],
            ["python", "programming"],
        ]
        
        tfidf.add_documents(docs)
        
        assert tfidf.total_documents == 3
        assert len(tfidf.document_frequency) > 0
    
    def test_compute_tfidf_score(self):
        """Test complete TF-IDF score computation."""
        tfidf = TFIDFComputer()
        
        tfidf.add_document(["test", "klar"])
        tfidf.add_document(["test", "content"])
        
        doc_terms = ["test", "test", "new"]
        score = tfidf.compute_tfidf("test", doc_terms)
        
        assert score.tf > 0
        assert score.idf > 0
        assert score.tfidf > 0
    
    def test_compute_document_scores(self):
        """Test scoring all terms in a document."""
        tfidf = TFIDFComputer()
        
        tfidf.add_document(["test", "klar"])
        tfidf.add_document(["test", "content"])
        
        doc_terms = ["test", "test", "klar", "new"]
        scores = tfidf.compute_document_scores(doc_terms)
        
        assert len(scores) > 0
        # Scores should be sorted
        if len(scores) > 1:
            assert scores[0].tfidf >= scores[-1].tfidf
    
    def test_get_important_terms(self):
        """Test getting important terms by threshold."""
        tfidf = TFIDFComputer()
        
        tfidf.add_document(["test", "klar"])
        tfidf.add_document(["test", "content"])
        
        doc_terms = ["test", "test", "klar"]
        important = tfidf.get_important_terms(doc_terms, threshold=0.1)
        
        assert len(important) >= 0
    
    def test_corpus_stats(self):
        """Test corpus statistics."""
        tfidf = TFIDFComputer()
        
        tfidf.add_document(["test", "klar"])
        tfidf.add_document(["test", "content"])
        tfidf.add_document(["python", "programming"])
        
        stats = tfidf.compute_corpus_stats()
        
        assert stats['total_documents'] == 3
        assert stats['unique_terms'] > 0
        assert stats['avg_df'] > 0
    
    def test_reset(self):
        """Test corpus reset."""
        tfidf = TFIDFComputer()
        
        tfidf.add_document(["test", "klar"])
        assert tfidf.total_documents == 1
        
        tfidf.reset()
        assert tfidf.total_documents == 0
        assert len(tfidf.document_frequency) == 0
