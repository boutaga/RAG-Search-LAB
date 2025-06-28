# **LangChain Modular RAG Walkthrough**

This lab demonstrates how LangChain separates the three key pieces of a Retrieval-Augmented Generation (RAG) workflow:

1. **Embedding** – converting text to vectors with `OpenAIEmbeddings`.
2. **Retrieval** – fetching relevant documents via `PGVector` and `SQLDatabase`.
3. **Prompting** – generating the final answer using `ChatOpenAI` in a `RetrievalQA` chain.

The `langchain_retrieval_qa.py` script wires these components together. It builds a vector store backed by PostgreSQL and uses LangChain's `RetrievalQA` to answer questions from the retrieved articles.

**Why use LangChain?**

Earlier labs (for example `qa_context_only.py`) handled embeddings, SQL queries and prompting manually. While that approach is explicit, it also leads to a lot of boilerplate. LangChain abstracts those steps into easily swappable modules so you can focus on the RAG logic instead of database calls or API formatting. The result is a shorter, more maintainable script that is easier to extend with different models or retrievers.

Before running the script, make sure LangChain is installed. See the environment setup in [LAB-setups.md](../LAB-setups.md) for creating a virtualenv and installing packages:

```bash
pip install langchain langchain-openai langchain-community
```

Run the lab with:

```bash
python labs/lab3/langchain_retrieval_qa.py
```
