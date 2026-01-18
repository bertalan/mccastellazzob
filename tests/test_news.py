"""
MC Castellazzo - News Page Tests (TDD)
======================================
Test per NewsIndexPage e NewsPage.
"""
import pytest
import uuid
from datetime import date

from django.contrib.auth import get_user_model
from wagtail.models import Page

from apps.website.models import HomePage


User = get_user_model()


@pytest.fixture
def news_index(site):
    """Create a NewsIndexPage under HomePage."""
    from apps.website.models import NewsIndexPage
    
    home = HomePage.objects.first()
    news_index = NewsIndexPage(
        title="Novità",
        slug=f"novita-{uuid.uuid4().hex[:8]}",
    )
    home.add_child(instance=news_index)
    return news_index


@pytest.fixture
def author_user(db):
    """Create a user to be article author."""
    return User.objects.create_user(
        username="autore_test",
        email="autore@test.com",
        first_name="Mario",
        last_name="Rossi",
        password="testpass123",
    )


@pytest.fixture
def news_article(news_index, author_user):
    """Create a NewsPage under NewsIndexPage."""
    from apps.website.models import NewsPage
    
    article = NewsPage(
        title="Raduno Primaverile 2026",
        slug=f"raduno-primaverile-{uuid.uuid4().hex[:8]}",
        author=author_user,
        author_display="Mario Rossi",
        date_display=date(2026, 1, 15),
    )
    news_index.add_child(instance=article)
    return article


@pytest.mark.django_db
class TestNewsIndexPage:
    """Tests for NewsIndexPage model."""
    
    def test_news_index_creation(self, news_index):
        """Test NewsIndexPage can be created."""
        assert news_index.pk is not None
        assert news_index.title == "Novità"
    
    def test_news_index_subpage_types(self, news_index):
        """Test NewsIndexPage only allows NewsPage as children."""
        from apps.website.models import NewsIndexPage
        
        assert "website.NewsPage" in NewsIndexPage.subpage_types
    
    def test_news_index_inherits_coderedcms(self, news_index):
        """Test NewsIndexPage inherits from CoderedArticleIndexPage."""
        from coderedcms.models import CoderedArticleIndexPage
        
        assert isinstance(news_index, CoderedArticleIndexPage)
    
    def test_news_index_has_pagination(self, news_index):
        """Test NewsIndexPage has pagination field from CodeRedCMS."""
        assert hasattr(news_index, 'index_num_per_page')
    
    def test_news_index_has_classifier_filter(self, news_index):
        """Test NewsIndexPage supports classifier filtering."""
        assert hasattr(news_index, 'index_classifiers')


@pytest.mark.django_db
class TestNewsPage:
    """Tests for NewsPage model."""
    
    def test_news_page_creation(self, news_article):
        """Test NewsPage can be created."""
        assert news_article.pk is not None
        assert news_article.title == "Raduno Primaverile 2026"
    
    def test_news_page_inherits_coderedcms(self, news_article):
        """Test NewsPage inherits from CoderedArticlePage."""
        from coderedcms.models import CoderedArticlePage
        
        assert isinstance(news_article, CoderedArticlePage)
    
    def test_news_page_has_author(self, news_article, author_user):
        """Test NewsPage has author field from CodeRedCMS."""
        assert news_article.author == author_user
        assert news_article.author_display == "Mario Rossi"
    
    def test_news_page_has_date(self, news_article):
        """Test NewsPage has date_display field."""
        assert news_article.date_display == date(2026, 1, 15)
    
    def test_news_page_has_gallery(self, news_article):
        """Test NewsPage has gallery StreamField."""
        assert hasattr(news_article, 'gallery')
    
    def test_news_page_has_cover_image(self, news_article):
        """Test NewsPage has cover_image from CodeRedCMS."""
        assert hasattr(news_article, 'cover_image')
    
    def test_news_page_has_tags(self, news_article):
        """Test NewsPage has tags from CodeRedCMS."""
        assert hasattr(news_article, 'tags')
    
    def test_news_page_has_classifier_terms(self, news_article):
        """Test NewsPage has classifier_terms for categories."""
        assert hasattr(news_article, 'classifier_terms')
    
    def test_news_page_parent_types(self):
        """Test NewsPage can only be child of NewsIndexPage."""
        from apps.website.models import NewsPage
        
        assert "website.NewsIndexPage" in NewsPage.parent_page_types


@pytest.mark.django_db
class TestNewsPageSchema:
    """Tests for NewsPage schema.org data."""
    
    def test_news_page_schema_type(self, news_article):
        """Test NewsPage schema.org type is Article."""
        assert news_article.get_json_ld_type() == "Article"
    
    def test_news_page_schema_has_headline(self, news_article):
        """Test NewsPage schema.org has headline."""
        data = news_article.get_json_ld_data()
        assert data.get("headline") == "Raduno Primaverile 2026"
    
    def test_news_page_schema_has_author(self, news_article):
        """Test NewsPage schema.org has author."""
        data = news_article.get_json_ld_data()
        assert "author" in data
        assert data["author"]["@type"] == "Person"
        assert data["author"]["name"] == "Mario Rossi"
    
    def test_news_page_schema_has_date(self, news_article):
        """Test NewsPage schema.org has datePublished."""
        data = news_article.get_json_ld_data()
        assert "datePublished" in data
