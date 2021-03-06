from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response

from reader.permissions import *
from reader.serializers import *
from rest_framework.pagination import *
from rest_framework import mixins

from search import api
from core import  models as core_model
from core import serializers as core_serializers

class ExamplePagination(PageNumberPagination):
    page_size = 20

class RecommendPagination(PageNumberPagination):
    page_size = 10


class recommend_article(generics.ListAPIView):
    """
    返回推荐的文章列表
    """

    pagination_class = RecommendPagination
    serializer_class = ArticleSerializer

    def exact(self, d):
        return d['raw']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset, userinfo = self.filter_queryset(self.get_queryset())

        dictionary = dict(zip(userinfo[2], userinfo[1]))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = sorted(serializer.data, key= lambda x: -dictionary[x['id']])
            print(data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data= sorted(serializer.data, key=lambda x: -dictionary[x['id']])
        print(data)
        return Response(data)


    def get_queryset(self):
        user = self.request.user
        print(user.id)
        userprofile= core_model.UserProfile.objects.get(user=user)
        serializer = core_serializers.UserWordlistSerializer(userprofile, context={'request': self.request})
        glossary=serializer.data['glossary']
        words= [self.exact(k) for k in glossary ]

        result=api.get_record(words,10)
        print(words)
        print(result)

        #ids = api.get_record()
        return Article.objects.all().filter(pk__in=result[2]).order_by('id') , result



class ArticleViewSet(viewsets.ModelViewSet):
    """
    list:
    返回新闻列表

    retrieve:
    返回某一条新闻

    create:
    创建一条新闻。只有管理员才有权限创建。

    delete:
    删除一条新闻。只有管理员才有权限删除。
    """

    def create(self, request):
        reply = super().create(request)
        api.put_record(reply.data['id'],
                       reply.data['title'],
                       reply.data['pub_date'],
                       reply.data['content'],
                       reply.data['img_url'],
                       reply.data['source'])
        return reply

    #    return super().create(request)

    def list(self, request):
        queryset = Article.objects.all().order_by('-pub_date')
        paginator = ExamplePagination()

        page = paginator.paginate_queryset(queryset,request)
        if page is not None:
            serializer = ArticleSerializer(page, context={'request': request}, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ArticleSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    queryset = Article.objects.all()
    serializer_class = DetailArticleSerializer
    pagination_class = ExamplePagination
    permission_classes = (IsAdminOrReadOnly,)

    # filter_fields = ('title','source')  # 暂时先不提供搜索功能
    # filter_fields = ('title','source')


# class DArticleViewSet(viewsets.ModelViewSet):
#     queryset = Article.objects.all()
#     serializer_class = DArticleSerializer
#     filter_fields = ('title',)


#    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

# class DArticleList(generics.ListCreateAPIView):
#     queryset = Article.objects.all()
#     serializer_class = DArticleSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)


# class DArticleDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Article.objects.all()
#     serializer_class = DArticleSerializer


class MediaViewSet(viewsets.ModelViewSet):
    """
    list:
    返回媒体列表。
    其他权限是所有人都能READ，管理员可以WRITE。
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = (IsAdminOrReadOnly,)
