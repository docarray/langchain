import numpy as np
import pytest

from langchain.schema import Document
from langchain.vectorstores.in_memory_exact_search import InMemoryExactSearch
from tests.integration_tests.vectorstores.fake_embeddings import FakeEmbeddings


def test_in_memory_vec_store_from_texts() -> None:
    """Test end to end construction and simple similarity search."""
    texts = ["foo", "bar", "baz"]
    docsearch = InMemoryExactSearch.from_texts(
        texts,
        FakeEmbeddings(),
    )
    assert isinstance(docsearch, InMemoryExactSearch)
    assert docsearch.doc_index.num_docs() == 3


def test_in_memory_vec_store_add_texts(tmp_path) -> None:
    """Test end to end construction and simple similarity search."""
    docsearch = InMemoryExactSearch(
        embedding=FakeEmbeddings(),
    )
    assert isinstance(docsearch, InMemoryExactSearch)
    assert docsearch.doc_index.num_docs() == 0

    texts = ["foo", "bar", "baz"]
    docsearch.add_texts(texts=texts)
    assert docsearch.doc_index.num_docs() == 3


@pytest.mark.parametrize('metric', ['cosine_sim', 'euclidean_dist', 'sqeuclidean_dist'])
def test_sim_search(metric) -> None:
    """Test end to end construction and simple similarity search."""
    texts = ["foo", "bar", "baz"]
    in_memory_vec_store = InMemoryExactSearch.from_texts(
        texts=texts,
        embedding=FakeEmbeddings(),
        metric=metric,
    )

    output = in_memory_vec_store.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo")]


@pytest.mark.parametrize('metric', ['cosine_sim', 'euclidean_dist', 'sqeuclidean_dist'])
def test_sim_search_with_score(metric) -> None:
    """Test end to end construction and similarity search with score."""
    texts = ["foo", "bar", "baz"]
    in_memory_vec_store = InMemoryExactSearch.from_texts(
        texts=texts,
        embedding=FakeEmbeddings(),
        metric=metric,
    )

    output = in_memory_vec_store.similarity_search_with_score("foo", k=1)

    out_doc, out_score = output[0]
    assert out_doc == Document(page_content="foo")

    expected_score = 0.0 if 'dist' in metric else 1.0
    assert np.isclose(out_score, expected_score, atol=1.e-6)


@pytest.mark.parametrize('metric', ['cosine_sim', 'euclidean_dist', 'sqeuclidean_dist'])
def test_sim_search_by_vector(metric) -> None:
    """Test end to end construction and similarity search by vector."""
    texts = ["foo", "bar", "baz"]
    in_memory_vec_store = InMemoryExactSearch.from_texts(
        texts=texts,
        embedding=FakeEmbeddings(),
        metric=metric,
    )

    embedding = [1.0] * 10
    output = in_memory_vec_store.similarity_search_by_vector(embedding, k=1)

    assert output == [Document(page_content="bar")]


@pytest.mark.parametrize('metric', ['cosine_sim', 'euclidean_dist', 'sqeuclidean_dist'])
def test_max_marginal_relevance_search(metric) -> None:
    """Test MRR search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": i} for i in range(len(texts))]
    docsearch = InMemoryExactSearch.from_texts(
        texts,
        FakeEmbeddings(),
        metadatas=metadatas,
        metric=metric
    )
    output = docsearch.max_marginal_relevance_search("foo", k=2, fetch_k=3)
    assert output == [
        Document(page_content="foo", metadata={"page": 0}),
        Document(page_content="bar", metadata={"page": 1}),
    ]
