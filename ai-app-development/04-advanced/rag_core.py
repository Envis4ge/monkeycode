"""
RAG 核心原理 — 从零实现检索增强生成
====================================
目标：理解 Embedding + 向量检索 + RAG 管道

核心概念：
- 文本分块 (Chunking)
- 向量化 (Embedding)
- 相似度检索 (Retrieval)
- RAG 管道 (Retrieval-Augmented Generation)
"""

import math
import re
from collections import Counter

# ============ 文本分块 ============

def chunk_text(text, chunk_size=200, overlap=50):
    """
    将长文本分成小块
    
    chunk_size: 每块的字符数
    overlap: 相邻块的重叠字符数（保持上下文连续性）
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # 尝试在句号或换行处分割
        if end < len(text):
            for sep in ['\n', '。', '.', '！', '!', '？', '?']:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size * 0.5:
                    end = start + last_sep + 1
                    chunk = text[start:end]
                    break
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if c]


# ============ TF-IDF 向量化 ============

class SimpleEmbedder:
    """
    简化版文本向量化 (TF-IDF)
    
    实际项目使用:
    - OpenAI Embeddings (text-embedding-3-small)
    - BGE (BAAI General Embedding)
    - M3E (中文优化)
    - Sentence-Transformers
    """
    
    def __init__(self):
        self.vocabulary = {}   # word → index
        self.idf = {}          # word → IDF score
        self.doc_count = 0
    
    def tokenize(self, text):
        """简单分词：中文逐字+二元组，英文按词"""
        text = text.lower()
        tokens = []
        for word in re.findall(r'[\w\u4e00-\u9fff]+', text):
            if any('\u4e00' <= c <= '\u9fff' for c in word):
                for i in range(len(word)):
                    tokens.append(word[i])
                    if i + 1 < len(word):
                        tokens.append(word[i:i+2])
            else:
                tokens.append(word)
        return tokens
    
    def fit(self, documents):
        """从文档集合学习词汇表和 IDF"""
        self.doc_count = len(documents)
        doc_freq = Counter()  # word → 出现在多少文档中
        
        for doc in documents:
            tokens = set(self.tokenize(doc))
            doc_freq.update(tokens)
        
        # 构建词汇表
        all_words = sorted(doc_freq.keys())
        self.vocabulary = {w: i for i, w in enumerate(all_words)}
        
        # 计算 IDF: log(N / df)
        for word, freq in doc_freq.items():
            self.idf[word] = math.log(self.doc_count / (freq + 1))
    
    def embed(self, text):
        """将文本转为 TF-IDF 向量"""
        tokens = self.tokenize(text)
        if not tokens:
            return [0.0] * len(self.vocabulary)
        
        # TF (词频)
        tf = Counter(tokens)
        total = sum(tf.values())
        
        # TF-IDF 向量
        vector = [0.0] * len(self.vocabulary)
        for word, count in tf.items():
            if word in self.vocabulary:
                idx = self.vocabulary[word]
                vector[idx] = (count / total) * self.idf.get(word, 0)
        
        return vector


# ============ 向量相似度 ============

def cosine_similarity(a, b):
    """余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ============ 向量存储 ============

class VectorStore:
    """
    简化版向量存储
    
    实际项目使用:
    - Chroma (轻量级)
    - FAISS (高性能)
    - Pinecone (云服务)
    - Milvus (企业级)
    """
    
    def __init__(self):
        self.vectors = []    # 向量列表
        self.texts = []      # 原始文本
    
    def add(self, text, vector):
        self.texts.append(text)
        self.vectors.append(vector)
    
    def search(self, query_vector, top_k=3):
        """搜索最相似的文档"""
        similarities = []
        for i, vec in enumerate(self.vectors):
            sim = cosine_similarity(query_vector, vec)
            similarities.append((sim, i))
        
        similarities.sort(reverse=True)
        return [
            {"text": self.texts[i], "score": sim}
            for sim, i in similarities[:top_k]
        ]


# ============ RAG 管道 ============

class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) 管道
    
    流程:
    1. 索引阶段: 文档 → 分块 → 向量化 → 存储
    2. 查询阶段: 问题 → 向量化 → 检索 → 拼接上下文 → 生成回答
    """
    
    def __init__(self, llm_func=None):
        self.embedder = SimpleEmbedder()
        self.store = VectorStore()
        self.llm_func = llm_func or self._default_llm
    
    def index(self, documents):
        """索引文档"""
        # 1. 分块
        all_chunks = []
        for doc in documents:
            chunks = chunk_text(doc, chunk_size=200, overlap=50)
            all_chunks.extend(chunks)
        
        # 2. 训练向量化器
        self.embedder.fit(all_chunks)
        
        # 3. 向量化并存储
        for chunk in all_chunks:
            vector = self.embedder.embed(chunk)
            self.store.add(chunk, vector)
        
        print(f"已索引 {len(all_chunks)} 个文本块")
    
    def query(self, question, top_k=3):
        """查询"""
        # 1. 向量化问题
        q_vector = self.embedder.embed(question)
        
        # 2. 检索相关文档
        results = self.store.search(q_vector, top_k=top_k)
        
        # 3. 拼接上下文
        context = "\n\n".join([r["text"] for r in results])
        
        # 4. 生成回答
        prompt = f"请根据以下信息回答问题。如果信息不足，请说明。\n\n参考信息:\n{context}\n\n问题: {question}\n\n回答:"
        answer = self.llm_func(prompt)
        
        return {
            "answer": answer,
            "sources": results,
            "context": context,
        }
    
    def _default_llm(self, prompt):
        """默认 LLM（模拟）"""
        return f"[模拟回答] 基于检索到的信息，关于'{prompt.split('问题:')[-1].strip()}'的回答..."


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("RAG 核心原理演示")
    print("=" * 60)
    
    # 示例文档
    documents = [
        """Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年发布。
        Python 设计哲学强调代码的可读性和简洁性，支持多种编程范式，
        包括面向对象、命令式、函数式编程。Python 是动态类型语言，
        拥有垃圾回收机制，能自动管理内存。""",
        
        """机器学习是人工智能的一个子领域，它使计算机能够从数据中学习，
        而无需显式编程。主要方法包括：监督学习（分类、回归）、
        无监督学习（聚类、降维）、强化学习（奖励驱动）。""",
        
        """RAG（检索增强生成）是一种结合信息检索和文本生成的技术。
        它先从知识库中检索相关文档，然后将检索结果作为上下文，
        让大语言模型生成有依据的回答，有效减少幻觉问题。""",
        
        """大语言模型（LLM）是基于 Transformer 架构的深度学习模型，
        通过大规模预训练学习语言模式。代表模型包括 GPT、LLaMA、Qwen 等。
        LLM 在推理、代码生成、翻译等任务上表现出色。""",
    ]
    
    # 创建 RAG 管道
    rag = RAGPipeline()
    
    # 索引文档
    print("\n--- 索引文档 ---")
    rag.index(documents)
    
    # 查询
    questions = [
        "Python 是什么？",
        "RAG 如何减少幻觉？",
        "机器学习有哪些方法？",
    ]
    
    for q in questions:
        print(f"\n问题: {q}")
        result = rag.query(q, top_k=2)
        print(f"检索到 {len(result['sources'])} 个相关片段:")
        for i, src in enumerate(result["sources"]):
            print(f"  [{i+1}] (相似度: {src['score']:.3f}) {src['text'][:50]}...")
        print(f"回答: {result['answer']}")
    
    print("\n✅ RAG 管道演示完成！")


if __name__ == '__main__':
    demo()
