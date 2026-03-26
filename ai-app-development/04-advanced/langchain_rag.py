"""
LangChain RAG 管道 — 用 LangChain 搭建 RAG
============================================
目标：掌握 LangChain 搭建 RAG 管道的完整流程

核心组件：
- Document Loaders（文档加载）
- Text Splitters（文本分割）
- Embeddings（向量化）
- Vector Stores（向量存储）
- Retrievers（检索器）
- Chains（处理链）
"""

# 注意：此文件展示四种 RAG 写法，仅第一种（纯实现）可直接运行
# 其余需要安装 LangChain: pip install langchain langchain-community

# ============ 写法1: 纯 Python 实现 ============

from collections import Counter
import math
import re

class PurePythonRAG:
    """
    不依赖任何框架的 RAG 实现
    适合理解原理
    """
    
    def __init__(self):
        self.documents = []
        self.vocabulary = {}
        self.idf = {}
    
    def _tokenize(self, text):
        return re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    
    def _tf_idf(self, text, doc_freq, n_docs):
        tokens = self._tokenize(text)
        tf = Counter(tokens)
        total = len(tokens) or 1
        vec = {}
        for w, c in tf.items():
            if w in self.vocabulary:
                vec[w] = (c / total) * math.log(n_docs / (doc_freq.get(w, 0) + 1))
        return vec
    
    def _cosine(self, a, b):
        common = set(a.keys()) & set(b.keys())
        dot = sum(a[k] * b[k] for k in common)
        norm_a = math.sqrt(sum(v**2 for v in a.values()))
        norm_b = math.sqrt(sum(v**2 for v in b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0
    
    def index(self, docs):
        self.documents = docs
        doc_freq = Counter()
        for doc in docs:
            doc_freq.update(set(self._tokenize(doc)))
        self.vocabulary = {w: i for i, w in enumerate(doc_freq)}
        self.idf = {w: math.log(len(docs) / (f + 1)) for w, f in doc_freq.items()}
    
    def query(self, question, top_k=2):
        q_vec = self._tf_idf(question, {}, len(self.documents))
        scores = []
        for i, doc in enumerate(self.documents):
            d_vec = self._tf_idf(doc, Counter(set(self._tokenize(d)) for d in [doc]), len(self.documents))
            scores.append((self._cosine(q_vec, d_vec), i))
        scores.sort(reverse=True)
        return [(self.documents[i], s) for s, i in scores[:top_k]]


def demo_pure():
    """纯 Python RAG 演示"""
    print("=" * 50)
    print("写法1: 纯 Python RAG")
    print("=" * 50)
    
    docs = [
        "Python是一种高级编程语言，由Guido van Rossum创建。",
        "机器学习是AI的子领域，让计算机从数据中学习。",
        "RAG结合检索和生成，减少大模型的幻觉问题。",
        "LangChain是构建LLM应用的Python框架。",
    ]
    
    rag = PurePythonRAG()
    rag.index(docs)
    
    for q in ["Python是什么？", "什么是RAG？"]:
        results = rag.query(q)
        print(f"\nQ: {q}")
        for doc, score in results:
            print(f"  [{score:.3f}] {doc}")


# ============ 写法2: LangChain 基础写法 ============

LANGCHAIN_BASIC = '''
# pip install langchain langchain-openai langchain-community chromadb

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# 1. 加载文档
loader = TextLoader("docs.txt")
documents = loader.load()

# 2. 分割文本
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 3. 向量化 + 存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# 4. 创建 RAG 链
llm = ChatOpenAI(model="gpt-4o-mini")
chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())

# 5. 查询
result = chain.invoke({"query": "Python的特点是什么？"})
print(result["result"])
'''


# ============ 写法3: LangChain + Ollama ============

LANGCHAIN_OLLAMA = '''
# pip install langchain langchain-ollama langchain-community chromadb

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# 使用本地 Ollama 模型
loader = TextLoader("docs.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 本地向量化 + 存储
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(chunks, embeddings)

# 本地 LLM
llm = ChatOllama(model="qwen2.5:7b")
chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())

result = chain.invoke({"query": "Python的特点是什么？"})
print(result["result"])
'''


# ============ 写法4: LCEL 写法（推荐） ============

LANGCHAIN_LCEL = '''
# pip install langchain langchain-openai chromadb

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 准备向量库
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 提示词模板
template = """根据以下上下文回答问题。如果不知道就说不知道。

上下文: {context}

问题: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-4o-mini")

# LCEL 管道（一行搞定）
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 查询
print(chain.invoke("Python是什么？"))
'''


# ============ 演示 ============

if __name__ == '__main__':
    demo_pure()
    
    print("\n" + "=" * 50)
    print("写法2: LangChain 基础写法")
    print("=" * 50)
    print(LANGCHAIN_BASIC)
    
    print("\n" + "=" * 50)
    print("写法3: LangChain + Ollama (本地部署)")
    print("=" * 50)
    print(LANGCHAIN_OLLAMA)
    
    print("\n" + "=" * 50)
    print("写法4: LCEL 管道写法 (推荐)")
    print("=" * 50)
    print(LANGCHAIN_LCEL)
