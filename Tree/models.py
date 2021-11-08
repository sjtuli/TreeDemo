from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import markdown
from django.utils.html import strip_tags
from mdeditor.fields import MDTextField #必须导入

# Create your models here.
#格式层层递进：
#树
#|
#节点
#|
#节点内容

class Department(models.Model):
    name = models.CharField(max_length=128, unique=False, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, db_constraint=False,
                               null=True, blank=True, verbose_name='父部门')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '路径树'
        verbose_name_plural = verbose_name #复数形式


class Tag(models.Model):
    """
    标签 Tag 也比较简单，和 Category 一样。
    再次强调一定要继承 models.Model 类！
    """
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name


class Node(models.Model):
    author = models.ForeignKey(User, related_name='nodes', verbose_name='回答者', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, verbose_name='节点', related_name='node', on_delete=models.CASCADE)
    # body = models.TextField('正文', default='')
    body =MDTextField('正文', default='')   #这样后台可以使用Markdown编辑器
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    def __str__(self):
        return str(self.department_id)
    class Meta:
        verbose_name = '叶子节点'
        verbose_name_plural = verbose_name
    def save(self,*args,**kwargs):
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
        self.excerpt = strip_tags(md.convert(self.body))[:54]
        super().save(*args,**kwargs)
    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数


def get_file_upload_path(instance, filename):
    # return '{username}/cover/{date}/{filename}'.format(username=instance.author.username,date=time.strftime('%Y/%m/%d', time.localtime()),filename=filename)
    return 'upload/{department}/{filename}'.format(department=instance.department_id, filename=filename)


class NodeFile(models.Model):
    File = models.FileField('文件路径', null=True, upload_to=get_file_upload_path, default='')
    File_name = models.CharField('文件名', null=True, default='', max_length=128)
    node = models.ForeignKey('Node', related_name="file", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, verbose_name='节点', null=True, default='', related_name='file', on_delete=models.CASCADE)
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})
    def __str__(self):
        return str(self.File_name)

    class Meta:
        verbose_name = '上传文件'
        verbose_name_plural = verbose_name  # 复数形式
