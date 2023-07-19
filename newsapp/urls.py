from django.urls import path
from newsapp.views import LoginView, home, CategoryView, FeedByCategoryView, SecondaryNews

#All the urls for the newsapp
urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('news/category/', CategoryView.as_view(), name='category'),
    path('news/feed/<int:category_id>/', FeedByCategoryView.as_view(), name='feed'),
    path('news/group/' , SecondaryNews.as_view(), name='secondary_news'),
]
