import json, markdown, os, re, random
from PIL import Image
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.contrib.auth.decorators import login_required
from .models import Department, Node, NodeFile


def tree(request):
    mList = Department.objects.all()   #tree information
    _data = [
        {
            'id': x.id,
            'name': x.name,
            'pId': x.parent.id if x.parent else 0,
            'open': 1
        } for x in mList
    ]
    return render(request, 'tree.html', context={'data':_data, })


# @login_required(login_url='/account/login')
def create(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if 'parent' in data:
            postdata = {
                "name": data['name'],
                "parent": Department.objects.get(id=data['parent']),
            }
        else:
            postdata = {
                "name": data['name'],
            }
        try:
            Department.objects.create(**postdata)
            return JsonResponse({'state': 1, 'message': '创建成功!'})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Create Error: ' + str(e)})


def delete(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            parent = Department.objects.get(id=data['parent'])
            parent.delete()
            return JsonResponse({'state': 1, 'message': '创建成功!'})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Create Error: ' + str(e)})


def node_detail(request, department_id):
    department = Department.objects.get(id=department_id)
    user = request.user
    if not department.node.filter():
        nodedata = {"department": department, "author": user}
        Node.objects.create(**nodedata)
        pass
    node = department.node.get()
    _nodefile = department.file.filter()
    # post = node
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        TocExtension(slugify=slugify),
    ])
    node.body = md.convert(node.body)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    node.toc = m.group(1) if m is not None else ' '

    mList = Department.objects.all()   #tree information
    _data = [
        {
            'id': x.id,
            'name': x.name,
            'pId': x.parent.id if x.parent else 0,
            'open': 1
        } for x in mList
    ]
    return render(request, 'content_node.html', context={'user': user, 'department': department, 'node': node,
                                                                   'data':_data, 'nodefile':_nodefile })


# @login_required(login_url='/account/login')
def modify_post(request, department_id):
    department = Department.objects.get(id=department_id)
    node = department.node.get()
    if request.method == 'GET':
        return render(request,"modify_post.html", locals())  # 需要编写修改答案模板
    else:
        # answer_form = AnswerForm(request.POST)
        # if answer_form.is_valid():
        node.body = request.POST.get('editormd-markdown-doc')
        node.save()
        return HttpResponseRedirect(reverse('tree:node', args=(department_id,)))


def upload_img(request):
    if request.method == "POST":
        data = request.FILES['editormd-image-file']
        # filename = request.FILES.get['editormd-image-file', None].name
        img = Image.open(data)
        width = img.width
        height = img.height
        rate = 1.0  # 压缩率

        # 根据图像大小设置压缩率
        if width >= 1500 or height >= 2000:
            rate = 0.3
        elif width >= 1000 or height >= 1000:
            rate = 0.5
        elif width >= 500 or height >= 500:
            rate = 0.9

        width = int(width * rate)  # 新的宽
        height = int(height * rate)  # 新的高

        img.thumbnail((width, height), Image.ANTIALIAS)  # 生成缩略图
        url = 'editor/' + data.name
        name = settings.MEDIA_ROOT + url
        if os.path.exists(name):
            (file, ext) = os.path.splitext(data.name)
            file = file + str(random.randint(1, 1000))
            data.name = file + ext
            url = 'editor/' + data.name
            name = settings.MEDIA_ROOT + url
        try:
            img.save(name)
            url = 'media/editor/' + data.name
            # url = '/static' + name.split('static')[-1]
            # url = name.split('static')[-1]
            return JsonResponse({"success": 1, "message": "成功", "url": url})
        except Exception as e:
            return JsonResponse({'success': 0, 'message': '上传失败'})



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload/')


class FileForm(forms.Form):
    myfile = forms.FileField(required=True)

def upload_file(request, department_id):
    if request.method == "POST":  # 请求方法为POST时，进行处理
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                #获取表单数据
                file = form.cleaned_data['myfile']
                filename = request.FILES.get("myfile", None).name
                #获取数据库数据
                department = Department.objects.get(id=department_id)
                node = department.node.get()
                postdata = {
                    "File": file,
                    "File_name": filename,
                    "node": node,
                    "department": department
                }
                NodeFile.objects.create(**postdata)
                return HttpResponseRedirect(reverse('tree:node', args=[department_id]))
                # return HttpResponse('file upload ok')
            except Exception as e:
                return JsonResponse({'state': 0, 'message': 'Create Error: ' + str(e)})
        else:
            form = FileForm()
            return JsonResponse({'state': 0, 'message': '请上传文件'})




# def upload_file(request, department_id):
#     if request.method == "POST":  # 请求方法为POST时，进行处理
#         myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
#         if not myFile:
#             return HttpResponse("no files for upload!")
#             # return JsonResponse({'state': 1, 'message': 'no files for upload!'})
#         department = Department.objects.get(id=department_id)
#         file_path = os.path.join(MEDIA_ROOT, myFile.name)
#
#         node = department.node.get()
#         node.File_path = file_path
#         node.File_name = myFile.name
#         node.save()
#
#         destination = open(os.path.join(MEDIA_ROOT, myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
#         for chunk in myFile.chunks():  # 分块写入文件
#             destination.write(chunk)
#         destination.close()
#         return HttpResponse("upload over!")


def download_file(request,department_id,pk):
    if pk:
        file_name = NodeFile.objects.get(pk=pk).File_name
        file = open(os.path.join(os.path.join(MEDIA_ROOT, str(department_id)), file_name), 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        filename = 'attachment; filename='+file_name
        response['Content-Disposition'] = filename.encode('utf-8', 'ISO-8859-1')  # 设定传输给客户端的文件名称
        return response

def delete_file(request,department_id,pk):
    try:
        file = NodeFile.objects.get(pk=pk)
        file.delete()
    except Exception as e:
        print('delete error is %s' %(e))
        return JsonResponse({'state': 0, 'message': 'Delete Error: ' + str(e)})
    # return HttpResponse("upload over!")
    return HttpResponseRedirect(reverse('tree:node', args=(department_id,)))
