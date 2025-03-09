import os
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Simple tokenization based on GPT-like models
# This is a simplification and won't match OpenAI's exact tokenization,
# but it's a reasonable approximation for limiting prompt size

def num_tokens_from_string(text: str) -> int:
    """
    Estimate the number of tokens in a string.
    
    This is a simplified implementation that approximates token count.
    For production use, consider using tiktoken or other official tokenizers.
    
    Args:
        text: Input text
        
    Returns:
        int: Approximate token count
    """
    try:
        # Try to use tiktoken if available (more accurate)
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding for recent GPT models
        return len(encoding.encode(text))
    except ImportError:
        # Fall back to simple approximation
        logger.warning("tiktoken not available, using simple token estimation")
        return simple_token_count(text)

def simple_token_count(text: str) -> int:
    """
    Simple token count estimation.
    
    Args:
        text: Input text
        
    Returns:
        int: Approximate token count
    """
    # Split on whitespace and punctuation
    # This is a rough approximation
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    
    # Adjust for GPT's subword tokenization
    # On average, 1 word is approximately 1.3 tokens
    return int(len(tokens) * 1.3)

def truncate_text_for_model(text: str, max_tokens: int, buffer: int = 100) -> str:
    """
    Truncate text to fit within a model's token limit.
    
    Args:
        text: Input text to truncate
        max_tokens: Maximum tokens allowed
        buffer: Buffer tokens to leave room for prompt and completion
        
    Returns:
        str: Truncated text
    """
    tokens = num_tokens_from_string(text)
    target_tokens = max_tokens - buffer
    
    if tokens <= target_tokens:
        return text
    
    # Simple proportional truncation
    ratio = target_tokens / tokens
    truncated_length = int(len(text) * ratio)
    
    # Ensure we truncate at a reasonable point
    truncated_text = text[:truncated_length]
    
    # Try to truncate at a paragraph or line boundary
    last_newline = truncated_text.rfind('\n')
    if last_newline > 0.8 * truncated_length:
        truncated_text = truncated_text[:last_newline]
    
    return truncated_text

def chunk_text(text: str, max_tokens: int, overlap: int = 100) -> List[str]:
    """
    Split text into chunks that fit within token limits.
    
    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Estimate the character length for max_tokens
    avg_chars_per_token = 4  # Approximate
    max_chars = max_tokens * avg_chars_per_token
    overlap_chars = overlap * avg_chars_per_token
    
    # Split text by paragraphs
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(para) > max_chars:
            # If we have content in the current chunk, add it to chunks
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Start a new chunk with this paragraph
            current_chunk = para
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Apply overlap
    overlapped_chunks = []
    
    for i, chunk in enumerate(chunks):
        if i > 0:
            # Get the end of the previous chunk for overlap
            prev_chunk = chunks[i-1]
            overlap_text = prev_chunk[-overlap_chars:] if len(prev_chunk) > overlap_chars else prev_chunk
            chunk = overlap_text + "\n\n" + chunk
        
        overlapped_chunks.append(chunk)
    
    return overlapped_chunks