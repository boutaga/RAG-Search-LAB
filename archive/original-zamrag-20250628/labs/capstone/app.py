import streamlit as st
import requests
import pandas as pd

st.sidebar.title("RAG Capstone")
page = st.sidebar.radio("Page", ("Search", "Metrics"))

search_url = st.sidebar.text_input("Search URL", "http://localhost:5000/search")
metrics_url = st.sidebar.text_input("Metrics URL", "http://localhost:5000/all_metrics")

if page == "Search":
    st.title("RAG Capstone Search")
    query = st.text_input("Enter your question:")
    search_mode = st.selectbox(
        "Search mode",
        ["rag_open", "rag_context_only", "cosine", "l2"],
        index=0,
    )
    filter_text = st.text_input("Filter titles containing:", "")
    page_size = st.number_input("Results per page", min_value=1, max_value=20, value=5)
    record_metrics = st.checkbox("Record metrics", True)

    if 'page' not in st.session_state:
        st.session_state.page = 1

    col1, col2 = st.columns(2)
    if col1.button("Previous"):
        if st.session_state.page > 1:
            st.session_state.page -= 1
    if col2.button("Next"):
        st.session_state.page += 1

    if st.button("Search"):
        st.session_state.page = 1

    if query:
        payload = {
            "query": query,
            "search_mode": search_mode,
            "filter": filter_text,
            "page": st.session_state.page,
            "page_size": page_size,
            "record_metrics": record_metrics,
        }
        try:
            resp = requests.post(search_url, json=payload, timeout=30)
            data = resp.json()
        except Exception as e:
            st.error(f"Request failed: {e}")
        else:
            if data.get("response_type") == "llm_answer":
                st.subheader("Answer")
                st.write(data.get("answer", "No answer"))
                sources = data.get("sources", [])
                if sources:
                    st.subheader("Sources")
                    for s in sources:
                        st.write(f"**{s['title']}**")
                        st.write(s['snippet'])
                        st.write("---")
            elif data.get("response_type") == "raw_sql":
                st.subheader("Results")
                st.write(data.get("results"))
            else:
                st.write(data)
            if data.get("metrics"):
                st.subheader("Run Metrics")
                m = data["metrics"]
                st.json(m)
                total = m.get("total_ms", 0)
                if total:
                    emb = m.get("embedding_ms", 0)
                    dbt = m.get("db_ms", 0)
                    llm = m.get("llm_ms", 0)
                    emb_p = emb / total * 100 if total else 0
                    db_p = dbt / total * 100 if total else 0
                    llm_p = llm / total * 100 if total else 0
                    bar = f"""
<div style='display:flex;width:100%;height:20px;border:1px solid #ccc'>
  <div style='width:{emb_p}%;background:#3498db' title='Embedding {emb:.2f} ms'></div>
  <div style='width:{db_p}%;background:#2ecc71' title='DB {dbt:.2f} ms'></div>
  <div style='width:{llm_p}%;background:#e74c3c' title='LLM {llm:.2f} ms'></div>
</div>"""
                    st.markdown(bar, unsafe_allow_html=True)
else:
    st.title("Query Metrics")
    try:
        resp = requests.get(metrics_url, timeout=30)
        metrics = resp.json()
        desc_resp = requests.get(f"{metrics_url.rsplit('/',1)[0]}/metric_descriptions", timeout=30)
        descriptions = desc_resp.json() if desc_resp.ok else {}
        if metrics:
            df = pd.DataFrame(metrics)
            headers = ''.join([f"<th title='{descriptions.get(c,'')}'>{c}</th>" for c in df.columns])
            rows = ''
            for _, r in df.iterrows():
                cells = ''.join([f"<td>{r[c]}</td>" for c in df.columns])
                rows += f"<tr>{cells}</tr>"
            html = f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.write("No metrics available")
    except Exception as e:
        st.error(f"Failed to load metrics: {e}")
