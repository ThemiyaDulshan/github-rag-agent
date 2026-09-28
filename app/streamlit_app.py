from pathlib import Path
import streamlit as st

from app.github_loader import (
    load_repository,
    parse_github_url
)
from app.vector_store import is_indexed_repository


BASE_REPOSITORY_PATH = Path(
    "data/repositories"
)


st.set_page_config(
    page_title="RepoLens",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>
    .stApp {
        background: #0d1117;
        color: #e6edf3;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.5rem 0 1.2rem 0;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: #f0f6fc;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #8b949e;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 650;
        color: #f0f6fc;
        margin-top: 1.4rem;
        margin-bottom: 0.8rem;
    }

    .repo-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 1.35rem 1.5rem;
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .repo-name {
        font-size: 1.25rem;
        font-weight: 650;
        color: #f0f6fc;
        margin-bottom: 0.35rem;
    }

    .repo-path {
        color: #8b949e;
        font-size: 0.9rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 0.75rem;
    }

    .status-ready {
        color: #3fb950;
        background: rgba(46, 160, 67, 0.15);
        border: 1px solid rgba(46, 160, 67, 0.35);
    }

    .status-indexed {
        color: #58a6ff;
        background: rgba(56, 139, 253, 0.12);
        border: 1px solid rgba(56, 139, 253, 0.3);
    }

    .question-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 1.4rem 1.5rem 1.5rem 1.5rem;
        margin-top: 1rem;
    }

    .answer-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 1.2rem;
    }

    .answer-header {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 1.05rem;
        font-weight: 650;
        color: #f0f6fc;
        margin-bottom: 1rem;
    }

    .footer {
        text-align: center;
        color: #6e7681;
        font-size: 0.82rem;
        padding-top: 2rem;
    }

    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 0.85rem 1rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #8b949e;
    }

    div[data-testid="stMetricValue"] {
        color: #f0f6fc;
    }

    .stTextInput > div > div > input {
        background: #0d1117;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 10px;
    }

    .stTextInput > div > div > input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 1px #58a6ff;
    }

    .stTextArea > div > div > textarea {
        background: #0d1117;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 10px;
        font-size: 0.95rem;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 1px #58a6ff;
    }

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 2.65rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #30363d;
    }

    hr {
        border-color: #21262d;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def get_repository_path(
    owner: str,
    repository: str
) -> Path:
    return (
        BASE_REPOSITORY_PATH
        / f"{owner}__{repository}"
    )


def load_repository_for_app(
    url: str
):
    metadata = parse_github_url(url)

    owner = metadata["owner"]
    repository = metadata["repository"]

    repository_path = get_repository_path(
        owner,
        repository
    )

    cached = is_indexed_repository(
        owner,
        repository
    )

    if (
        st.session_state.get("repository_url")
        == url
        and st.session_state.get("repository_path")
        and Path(
            st.session_state.repository_path
        ).exists()
    ):
        return None

    if cached:
        st.info(
            "Existing index found. Reusing cached embeddings."
        )
    else:
        st.info(
            "First-time setup. Cloning and indexing repository..."
        )

    result = load_repository(
        url,
        str(repository_path)
    )

    st.session_state.repository_url = url
    st.session_state.repository_path = result[
        "repository_path"
    ]
    st.session_state.repository = result

    return result


if "repository_url" not in st.session_state:
    st.session_state.repository_url = ""

if "repository_path" not in st.session_state:
    st.session_state.repository_path = ""

if "repository" not in st.session_state:
    st.session_state.repository = None


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🔎 RepoLens</div>
        <div class="hero-subtitle">
            Understand any GitHub repository with AI-powered code search and analysis.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-title">Repository</div>',
    unsafe_allow_html=True
)


repository_url = st.text_input(
    "GitHub repository URL",
    value=st.session_state.repository_url,
    placeholder="https://github.com/pallets/flask",
    label_visibility="collapsed"
)


if st.button(
    "Load Repository",
    type="primary",
    use_container_width=True
):
    if not repository_url.strip():
        st.error(
            "Please enter a GitHub repository URL."
        )
    else:
        try:
            with st.spinner(
                "Loading repository..."
            ):
                result = load_repository_for_app(
                    repository_url.strip()
                )

            if result is None:
                st.success(
                    "Repository is already loaded."
                )
            elif result.get("cached"):
                st.success(
                    "Repository loaded from cache."
                )
            else:
                st.success(
                    "Repository indexed successfully."
                )

        except Exception as error:
            st.error(
                f"Failed to load repository: {error}"
            )


repository = st.session_state.repository


if repository:
    st.markdown(
        f"""
        <div class="repo-card">
            <div class="repo-name">
                📦 {repository["owner"]}/{repository["repository"]}
            </div>
            <div class="repo-path">
                Read-only repository analysis
            </div>
            <div class="status-badge status-ready">
                ● Ready
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Files",
            repository["total_files"]
        )

    with col2:
        st.metric(
            "Relevant Files",
            repository["relevant_files"]
        )

    with col3:
        st.metric(
            "Code Chunks",
            repository["index"]["chunks"]
        )

    with col4:
        st.metric(
            "Embeddings",
            repository["index"]["embeddings"]
        )

    st.markdown(
        '<div class="section-title">Ask about the codebase</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="question-card">',
        unsafe_allow_html=True
    )

    question = st.text_area(
        "Ask a question",
        placeholder=(
            "Example: Where is the Flask class implemented, "
            "and how does it handle incoming HTTP requests?"
        ),
        height=120,
        label_visibility="collapsed"
    )

    ask_question = st.button(
        "Ask RepoLens  →",
        type="primary",
        use_container_width=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    if ask_question:
        if not question.strip():
            st.warning(
                "Please enter a question."
            )
        else:
            from app.basic_graph import build_graph

            try:
                with st.spinner(
                    "Analyzing the codebase..."
                ):
                    graph = build_graph(
                        repository["repository_path"]
                    )

                    result = graph.invoke({
                        "question": question.strip(),
                        "repository_path": repository[
                            "repository_path"
                        ],
                        "messages": [],
                        "answer": "",
                        "tool_calls": []
                    })

                st.markdown(
                    """
                    <div class="answer-card">
                        <div class="answer-header">
                            💡 Answer
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    result["answer"]
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            except Exception as error:
                st.error(
                    f"Failed to answer question: {error}"
                )


st.markdown(
    """
    <div class="footer">
        RepoLens · GitHub Repository Analysis
    </div>
    """,
    unsafe_allow_html=True
)