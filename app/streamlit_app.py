from pathlib import Path
import os
import shutil
import stat

import streamlit as st

from app.basic_graph import build_graph
from app.github_loader import load_repository


st.set_page_config(
    page_title="GitHub Repository RAG Assistant",
    page_icon="🔎",
    layout="wide"
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

    if "repository_info" not in st.session_state:
        st.session_state.repository_info = None

    if "graph" not in st.session_state:
        st.session_state.graph = None

    if "messages" not in st.session_state:
        st.session_state.messages = []


def load_repository_for_app(url):
    destination = Path("data/repositories/current")

    remove_repository(destination)

    repository = load_repository(
        url,
        str(destination)
    )

    st.session_state.repository_path = str(destination)
    st.session_state.repository_name = repository["repository"]
    st.session_state.repository_info = repository
    st.session_state.graph = build_graph(str(destination))
    st.session_state.messages = []


def main():
    initialize_state()

    st.title("🔎 GitHub Repository RAG Assistant")

    st.write(
        "Ask questions about a GitHub repository using "
        "retrieval-augmented generation."
    )

    st.subheader("Repository")

    repository_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/pallets/flask"
    )

    if st.button(
        "Load Repository",
        type="primary"
    ):
        if not repository_url.strip():
            st.error("Please enter a GitHub repository URL.")
        else:
            try:
                with st.spinner(
                    "Cloning, analyzing, and indexing repository..."
                ):
                    load_repository_for_app(
                        repository_url.strip()
                    )

                st.success(
                    f"Repository '{st.session_state.repository_name}' "
                    "is ready."
                )

            except Exception as error:
                st.error(
                    f"Failed to load repository: {error}"
                )

    if st.session_state.repository_info:
        repository = st.session_state.repository_info
        index = repository["index"]

        st.divider()

        st.subheader("Repository Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Repository",
                st.session_state.repository_name
            )

        with col2:
            st.metric(
                "Documents",
                index["documents"]
            )

        with col3:
            st.metric(
                "Chunks",
                index["chunks"]
            )

        st.success("Repository indexed and ready for questions.")

        st.divider()

        st.subheader("Ask a Question")

        question = st.text_area(
            "Question",
            placeholder=(
                "Example: How does Flask handle an incoming HTTP request?"
            ),
            height=100
        )

        if st.button(
            "Ask",
            type="primary"
        ):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
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

                except Exception as error:
                    st.error(
                        f"Failed to answer question: {error}"
                    )

        if st.session_state.messages:
            st.divider()

            st.subheader("Answers")

            for message in reversed(
                st.session_state.messages
            ):
                st.markdown(
                    f"**Question:** {message['question']}"
                )

                st.markdown(message["answer"])

                st.divider()


if __name__ == "__main__":
    main()