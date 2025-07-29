from django.contrib import admin
from courses.models import Category, Course, Module, Lesson
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display= ('Name', 'slug')
    prepopulated_fields= {'slug': ['Name']}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display= ('title', 'instructor', 'category', 'price', 'is_published', 'created_at')
    list_filter= ['is_published', 'category', 'instructor']
    search_fields= ['title', 'description']
    prepopulated_fields= {'slug': ['title']}
    raw_id_fields= ['instructor']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display= ('title', 'course', 'order')
    list_filter= ['course']
    search_fields= ['title', 'description']
    ordering = ('course', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display= ('title', 'module', 'content_type', 'order', 'is_published', 'created_at')
    list_filter= ['module__course', 'content_type', 'is_published']
    search_fields= ['title', 'text_content']
    prepopulated_fields= {'slug': ['title']}
    ordering =('module', 'order')
