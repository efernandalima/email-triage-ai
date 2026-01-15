"""
Advanced NLP processing module for email classification.
Implements stopword removal, stemming, and text normalization.
"""

import re
from typing import List, Optional
import unicodedata

# Try to import NLTK (optional dependency)
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import RSLPStemmer  # Portuguese stemmer
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
    
    # Download required NLTK data (only first time)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        
    try:
        nltk.data.find('stemmers/rslp')
    except LookupError:
        nltk.download('rslp', quiet=True)
        
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not available. Using basic text processing.")


class EmailNLPProcessor:
    """
    Advanced NLP processor for email content.
    Supports Portuguese and English.
    """
    
    def __init__(self, language: str = 'portuguese'):
        """
        Initialize NLP processor.
        
        Args:
            language: 'portuguese' or 'english'
        """
        self.language = language
        
        # Initialize NLTK components if available
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words(language))
                self.stemmer = RSLPStemmer() if language == 'portuguese' else None
            except:
                self.stop_words = set()
                self.stemmer = None
        else:
            # Fallback: manual stopwords for Portuguese
            self.stop_words = self._get_manual_stopwords()
            self.stemmer = None
    
    def _get_manual_stopwords(self) -> set:
        """
        Manual stopwords list (fallback when NLTK not available).
        """
        portuguese_stopwords = {
            'a', 'o', 'e', 'é', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as',
            'dos', 'das', 'para', 'com', 'por', 'ao', 'aos', 'à', 'às', 'no', 'na',
            'nos', 'nas', 'que', 'se', 'não', 'ou', 'mais', 'como', 'mas', 'foi',
            'ser', 'tem', 'são', 'seu', 'sua', 'seus', 'suas', 'este', 'esta',
            'esse', 'essa', 'isto', 'isso', 'já', 'quando', 'muito', 'nos', 'eu',
            'ele', 'ela', 'nós', 'eles', 'elas', 'você', 'vocês', 'meu', 'minha'
        }
        return portuguese_stopwords
    
    def clean_text(self, text: str) -> str:
        """
        Advanced text cleaning with multiple normalization steps.
        
        Args:
            text: Raw email text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # 1. Normalize Unicode characters (remove accents if needed)
        # text = unicodedata.normalize('NFKD', text)
        
        # 2. Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 3. Remove email addresses (preserve privacy)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # 4. Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', text)
        text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),])+', '[URL]', text)
        
        # 5. Remove phone numbers
        text = re.sub(r'\(?\d{2,3}\)?[\s-]?\d{4,5}[\s-]?\d{4}', '[PHONE]', text)
        
        # 6. Remove CPF/CNPJ (Brazilian documents)
        text = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF]', text)
        text = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '[CNPJ]', text)
        
        # 7. Normalize currency mentions
        text = re.sub(r'R\$\s*\d+[.,]?\d*', '[VALOR]', text)
        
        # 8. Remove excessive punctuation
        text = re.sub(r'([!?.]){2,}', r'\1', text)
        
        # 9. Remove excessive newlines (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 10. Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # 11. Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # 12. Remove empty lines at start/end
        text = text.strip()
        
        return text
    
    def remove_stopwords(self, text: str) -> str:
        """
        Remove common stopwords that don't add semantic value.
        
        Args:
            text: Input text
            
        Returns:
            Text without stopwords
        """
        if not self.stop_words:
            return text
        
        # Tokenize (split into words)
        if NLTK_AVAILABLE:
            try:
                words = word_tokenize(text, language=self.language)
            except:
                words = text.split()
        else:
            words = text.split()
        
        # Filter out stopwords (but keep important punctuation)
        filtered_words = []
        for word in words:
            if word.lower() not in self.stop_words or len(word) <= 2:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def apply_stemming(self, text: str) -> str:
        """
        Apply stemming to reduce words to their root form.
        Example: "pagamento" -> "pag", "pagamentos" -> "pag"
        
        Args:
            text: Input text
            
        Returns:
            Stemmed text
        """
        if not self.stemmer:
            return text
        
        words = text.split()
        stemmed_words = []
        
        for word in words:
            # Don't stem very short words or special tokens
            if len(word) > 3 and not word.startswith('['):
                try:
                    stemmed_words.append(self.stemmer.stem(word))
                except:
                    stemmed_words.append(word)
            else:
                stemmed_words.append(word)
        
        return ' '.join(stemmed_words)
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract most relevant keywords from text.
        Uses simple frequency-based approach.
        
        Args:
            text: Input text
            top_n: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Clean and tokenize
        cleaned = self.clean_text(text)
        words = cleaned.lower().split()
        
        # Count word frequency (excluding stopwords)
        word_freq = {}
        for word in words:
            if (len(word) > 3 and 
                word.isalpha() and 
                word not in self.stop_words):
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_n]]
    
    def process_email(
        self, 
        text: str, 
        remove_stops: bool = True,
        apply_stem: bool = False,
        normalize_case: bool = False
    ) -> str:
        """
        Complete NLP pipeline for email processing.
        
        Args:
            text: Raw email text
            remove_stops: Whether to remove stopwords
            apply_stem: Whether to apply stemming
            normalize_case: Whether to convert to lowercase
            
        Returns:
            Processed text ready for classification
        """
        if not text:
            return ""
        
        # Step 1: Clean text (always)
        processed = self.clean_text(text)
        
        # Step 2: Normalize case (optional)
        if normalize_case:
            processed = processed.lower()
        
        # Step 3: Remove stopwords (optional)
        if remove_stops:
            processed = self.remove_stopwords(processed)
        
        # Step 4: Apply stemming (optional)
        if apply_stem and NLTK_AVAILABLE:
            processed = self.apply_stemming(processed)
        
        return processed


# =============================================================================
# BACKWARD COMPATIBLE FUNCTIONS (for existing code)
# =============================================================================

# Global processor instance
_global_processor = EmailNLPProcessor(language='portuguese')


def clean_text(text: str) -> str:
    """
    Basic text cleaning (backward compatible).
    Enhanced version with advanced NLP.
    
    Args:
        text: Raw email text
        
    Returns:
        Cleaned text
    """
    return _global_processor.clean_text(text)


def preprocess_email(
    text: str,
    remove_stopwords: bool = False,
    apply_stemming: bool = False
) -> str:
    """
    Advanced email preprocessing with optional NLP features.
    
    Args:
        text: Raw email text
        remove_stopwords: Remove common words
        apply_stemming: Reduce words to root form
        
    Returns:
        Processed text
    """
    return _global_processor.process_email(
        text,
        remove_stops=remove_stopwords,
        apply_stem=apply_stemming,
        normalize_case=False
    )


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract key terms from email content.
    
    Args:
        text: Email text
        top_n: Number of keywords
        
    Returns:
        List of relevant keywords
    """
    return _global_processor.extract_keywords(text, top_n)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Test the processor
    sample_email = """
    Prezados,
    
    Estamos enfrentando um erro crítico no sistema de pagamentos desde hoje às 14h.
    O erro ocorre quando tentamos processar transações acima de R$ 1.000,00.
    
    Nosso email de contato é suporte@empresa.com.br e telefone (11) 98765-4321.
    
    Segue em anexo o log completo. Aguardamos retorno urgente!
    
    Atenciosamente,
    João Silva
    """
    
    processor = EmailNLPProcessor()
    
    print("=" * 60)
    print("TEXTO ORIGINAL:")
    print(sample_email)
    
    print("\n" + "=" * 60)
    print("TEXTO LIMPO:")
    cleaned = processor.clean_text(sample_email)
    print(cleaned)
    
    print("\n" + "=" * 60)
    print("SEM STOPWORDS:")
    no_stops = processor.remove_stopwords(cleaned)
    print(no_stops)
    
    print("\n" + "=" * 60)
    print("KEYWORDS EXTRAÍDAS:")
    keywords = processor.extract_keywords(sample_email)
    print(keywords)
    
    print("\n" + "=" * 60)
    print("PROCESSAMENTO COMPLETO:")
    full_process = processor.process_email(
        sample_email,
        remove_stops=True,
        apply_stem=True
    )
    print(full_process)