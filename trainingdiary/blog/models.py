# from django.db import models
# from django import forms
# from wagtail.core.models import Page
# from wagtail.core.fields import RichTextField
# from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
# from wagtail.search import index
# from wagtail.snippets.models import register_snippet
# from wagtail.images.edit_handlers import ImageChooserPanel
#
# from modelcluster.fields import ParentalKey, ParentalManyToManyField
# from modelcluster.contrib.taggit import ClusterTaggableManager
# from taggit.models import TaggedItemBase
#
#
# @register_snippet
# class BlogCategory(models.Model):
#     name = models.CharField(max_length=255)
#     icon = models.ForeignKey(
#         'wagtailimages.Image', null=True, blank=True,
#         on_delete=models.SET_NULL, related_name='+'
#     )
#
#     panels = [
#         FieldPanel('name'),
#         ImageChooserPanel('icon'),
#     ]
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = 'blog categories'
#
#
# class BlogIndexPage(Page):
#     intro = RichTextField(blank=True)
#
#     content_panels = Page.content_panels + [
#         FieldPanel('intro', classname="full")
#     ]
#
#     def get_context(self, request):
#         # Update context to include only published posts, ordered by reverse-chron
#         context = super().get_context(request)
#         blogpages = self.get_children().live().order_by('-first_published_at')
#         context['blogpages'] = blogpages
#         return context
#
#
# class BlogPageTag(TaggedItemBase):
#     content_object = ParentalKey(
#         'BlogPage',
#         related_name='tagged_items',
#         on_delete=models.CASCADE
#     )
#
#
# class BlogPage(Page):
#     date = models.DateField("Post date")
#     intro = models.CharField(max_length=250)
#     body = RichTextField(blank=True)
#     tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
#     categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
#
#     search_fields = Page.search_fields + [
#         index.SearchField('intro'),
#         index.SearchField('body'),
#     ]
#
#     content_panels = Page.content_panels + [
#         MultiFieldPanel([
#             FieldPanel('date'),
#             FieldPanel('tags'),
#             FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
#         ], heading="Blog information"),
#         FieldPanel('intro'),
#         FieldPanel('body'),
#     ]
#
#
# class StandardPage(BlogPage):
#     pass
#
#
# class BlogTagIndexPage(Page):
#
#     def get_context(self, request):
#
#         # Filter by tag
#         tag = request.GET.get('tag')
#         blogpages = BlogPage.objects.filter(tags__name=tag)
#
#         # Update template context
#         context = super().get_context(request)
#         context['blogpages'] = blogpages
#         return context
#
#
# class BlogCategoryIndexPage(Page):
#
#     def get_context(self, request):
#         # Filter by tag
#         category = request.GET.get('category')
#         blogpages = BlogPage.objects.filter(categories__name=category)
#
#         # Update template context
#         context = super().get_context(request)
#         context['blogpages'] = blogpages
#         return context
