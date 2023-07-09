from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import reverse, redirect

from .models import Post, Category, Subscriber, SubscriberCategory
from .forms import PostForm
from .filters import PostFilter
from .tasks import notify_post


class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    ordering = "-date_create"
    paginate_by = 10

    def get_queryset(self):
        queryset = self.model.objects.all()
        url = self.request.get_full_path()
        if "search" in url:
            queryset = queryset.order_by("-date_create")
        elif "news" in url:
            queryset = queryset.filter(type="Новость").order_by("-date_create")
        elif "articles" in url:
            queryset = queryset.filter(type="Статья").order_by("-date_create")
        else:
            queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = "post_form.html"
    form_class = PostForm
    permission_required = ("news.add_post",)
    # raise_exception = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        url = self.request.get_full_path()
        if "news" in url:
            obj.type = "Новость"
        elif "articles" in url:
            obj.type = "Статья"
        obj.save()                          
        notify_post.delay(obj.id)
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_form.html"
    permission_required = ("news.change_post",)

    def get_success_url(self):
        url = self.request.get_full_path()
        if "news" in url:
            return reverse("news_detail", kwargs={"pk": self.kwargs.get("pk")})
        elif "articles" in url:
            return reverse("article_detail", kwargs={"pk": self.kwargs.get("pk")})
        else:
            return reverse("post_list")


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "post_delete.html"
    permission_required = ("news.delete_post",)

    def get_success_url(self):
        url = self.request.get_full_path()
        if "news" in url:
            return reverse("news_list")
        elif "articles" in url:
            return reverse("article_list")
        else:
            return reverse("post_list")


# class CategoryListView(ListView):
#     model = Category
#     template_name = "category_list.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["is_subscriptions"] = [
#             i.get("category__name")
#             for i in SubscriberCategory.objects.filter(
#                 subscriber__user=self.request.user
#             ).values("category__name")
#         ]
#         return context


class SubscriptionListView(ListView):
    model = SubscriberCategory
    template_name = "subscription_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["is_subscriptions"] = [
            i.get("category__name")
            for i in SubscriberCategory.objects.filter(
                subscriber__user=self.request.user
            ).values("category__name")
        ]
        return context


class SubscriberUpdateView(LoginRequiredMixin, UpdateView):
    model = Subscriber    

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")        
        if action == "sub":                    
            if not Subscriber.objects.filter(user=self.request.user).exists():                
                Subscriber.objects.create(user=self.request.user)
                Subscriber.objects.get(user=self.request.user).category.add(
                    self.kwargs.get("pk")
                )
            else:                
                Subscriber.objects.get(user=self.request.user).category.add(
                    self.kwargs.get("pk")
                )
        else:
            Subscriber.objects.get(user=self.request.user).category.remove(
                self.kwargs.get("pk")
            )
        return redirect(request.META.get("HTTP_REFERER"))
        # if (
        #     not Subscriber.objects.get(user=self.request.user)
        #     .category.filter(pk=self.kwargs.get("pk"))
        #     .exists()
        # ):
        #     print("not subscription!!!")
        #     Category.objects.get(slug=self.kwargs.get('slug')).subscribers.add(self.request.user)
        # else:
        #     Category.objects.get(slug=self.kwargs.get('slug')).subscribers.remove(self.request.user)
        # return redirect(request.META.get('HTTP_REFERER'))
