from pathlib import Path
import os
import shutil
import stat

import streamlit as st

from app.basic_graph import build_graph
from app.github_loader import load_repository
from app.vector_store import is_indexed_repository


st.set_page_config(
    page_title="RepoLens",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_repository(destination):
    if destination.exists():
        shutil.rmtree(
            destination,
            onerror=remove_readonly
        )


def initialize_state():
    if "repository_path" not in st.session_state:
        st.session_state.repository_path = None

    if "repository_name" not in st.session_state:
        st.session_state.repository_name = None

    if "repository_url" not in st.session_state:
        st.session_state.repository_url = None

    if "repository_info" not in st.session_state:
        st.session_state.repository_info = None

    if "graph" not in st.session_state:
        st.session_state.graph = None

    if "messages" not in st.session_state:
        st.session_state.messages = []


def load_repository_for_app(url):
    destination = Path("data/repositories/current")

    if (
        st.session_state.repository_url == url
        and st.session_state.repository_info is not None
        and st.session_state.repository_path is not None
        and destination.exists()
    ):
        return False

    from urllib.parse import urlparse

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError(
            "URL must contain an owner and repository name"
        )

    owner = parts[0]
    repository = parts[1]

    if repository.endswith(".git"):
        repository = repository[:-4]

    cached = is_indexed_repository(
        owner,
        repository
    )

    if cached:
        if not destination.exists():
            raise RuntimeError(
                "A cached index exists, but the repository files "
                "are not available. Please remove the cached index "
                "and reload the repository."
            )

        repository_info = load_repository(
            url,
            str(destination)
        )

        st.session_state.repository_path = str(destination)
        st.session_state.repository_name = repository_info["repository"]
        st.session_state.repository_url = url
        st.session_state.repository_info = repository_info
        st.session_state.graph = build_graph(str(destination))
        st.session_state.messages = []

        return True

    remove_repository(destination)

    repository_info = load_repository(
        url,
        str(destination)
    )

    st.session_state.repository_path = str(destination)
    st.session_state.repository_name = repository_info["repository"]
    st.session_state.repository_url = url
    st.session_state.repository_info = repository_info
    st.session_state.graph = build_graph(str(destination))
    st.session_state.messages = []

    return True


def inject_styles():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        .hero {
            padding: 0.5rem 0 1.5rem 0;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin-bottom: 0.35rem;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #6b7280;
            max-width: 720px;
            line-height: 1.6;
        }

        .section-label {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }

        .status-card {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
        }

        .status-title {
            font-size: 1.05rem;
            font-weight: 650;
            margin-bottom: 0.25rem;
        }

        .status-subtitle {
            color: #6b7280;
            font-size: 0.9rem;
        }

        .ready-badge {
            display: inline-block;
            margin-top: 0.75rem;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 650;
            background: rgba(34, 197, 94, 0.12);
            color: #16a34a;
        }

        .answer-card {
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 14px;
            padding: 1.25rem 1.35rem;
            margin: 0.8rem 0 1rem 0;
        }

        .question-label {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #6b7280;
            margin-bottom: 0.35rem;
        }

        .question-text {
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.5;
        }

        div[data-testid="stMetric"] {
            padding: 0.4rem 0;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 10px;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 10px;
        }

        .stButton > button {
            border-radius: 9px;
            font-weight: 600;
            min-height: 2.5rem;
        }

        .footer {
            text-align: center;
            color: #9ca3af;
            font-size: 0.8rem;
            margin-top: 3rem;
            padding-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">🔎 RepoLens</div>
            <div class="hero-subtitle">
                Understand GitHub repositories using semantic search,
                code analysis, and retrieval-augmented generation.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_repository_section():
    st.markdown(
        '<div class="section-label">Repository</div>',
        unsafe_allow_html=True
    )

    repository_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/pallets/flask",
        value=st.session_state.repository_url or "",
        label_visibility="collapsed"
    )

    if st.button(
        "Load Repository",
        type="primary",
        use_container_width=True
    ):
        if not repository_url.strip():
            st.error("Please enter a GitHub repository URL.")
        else:
            try:
                url = repository_url.strip()

                with st.spinner(
                    "Loading repository..."
                ):
                    loaded = load_repository_for_app(url)

                if loaded:
                    st.success(
                        f"'{st.session_state.repository_name}' "
                        "is ready."
                    )
                else:
                    st.info(
                        f"'{st.session_state.repository_name}' "
                        "is already loaded."
                    )

            except Exception as error:
                st.error(
                    f"Failed to load repository: {error}"
                )


def render_repository_status():
    repository = st.session_state.repository_info

    if not repository:
        return

    index = repository["index"]

    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-title">
                {st.session_state.repository_name}
            </div>
            <div class="status-subtitle">
                Repository indexed successfully
            </div>
            <div class="ready-badge">
                ● Ready
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Documents",
            index["documents"]
        )

    with col2:
        st.metric(
            "Code chunks",
            index["chunks"]
        )

    with col3:
        st.metric(
            "Embedding size",
            index["dimensions"]
        )


def ask_question(question):
    with st.spinner("Analyzing repository..."):
        result = st.session_state.graph.invoke({
            "question": question.strip(),
            "repository_path": (
                st.session_state.repository_path
            ),
            "messages": [],
            "answer": "",
            "tool_calls": []
        })

    st.session_state.messages.append({
        "question": question.strip(),
        "answer": result["answer"]
    })


def render_question_section():
    st.markdown(
        '<div class="section-label">Ask about the codebase</div>',
        unsafe_allow_html=True
    )

    question = st.text_area(
        "Question",
        placeholder=(
            "How does this repository handle an incoming HTTP request?"
        ),
        height=110,
        label_visibility="collapsed"
    )

    if st.button(
        "Ask Question",
        type="primary",
        use_container_width=True
    ):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                ask_question(question)
            except Exception as error:
                st.error(
                    f"Failed to answer question: {error}"
                )


def render_answers():
    if not st.session_state.messages:
        return

    st.markdown(
        '<div class="section-label">Conversation</div>',
        unsafe_allow_html=True
    )

    for message in reversed(
        st.session_state.messages
    ):
        st.markdown(
            f"""
            <div class="answer-card">
                <div class="question-label">
                    Question
                </div>
                <div class="question-text">
                    {message["question"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            message["answer"]
        )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            RepoLens · GitHub Repository RAG Assistant
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    initialize_state()
    inject_styles()
    render_header()

    render_repository_section()

    if st.session_state.repository_info:
        st.divider()
        render_repository_status()

        st.divider()
        render_question_section()

        render_answers()

    render_footer()


if __name__ == "__main__":
    main()