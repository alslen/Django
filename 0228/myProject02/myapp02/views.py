from django.shortcuts import render, redirect
from myapp02.models import Board
from django.views.decorators.csrf import csrf_exempt
import math


# Create your views here.
UPLOAD_DIR ='D:\\DJANGOWORK\\upload\\'

# write_form
def write_form(request):
    return render(request, "board/insert.html")

# insert
@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chuck in file.chunks():
            fp.write(chuck)
        fp.close()

    board = Board(writer= request.POST['writer'], title = request.POST['title'], content=request.POST['content'], 
                filename=fname, filesize=fsize)
    board.save()
    return redirect('/list')

# list
def list(request):

    boardCount = Board.objects.all().count()
    # 페이징 처리
    page = request.GET.get('page', 1)

    pageSize = 5
    blockPage = 3
    currentPage = int(page)
    totPage = math.ceil(boardCount/pageSize)
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1
    endPage = startPage+blockPage-1

    if endPage > totPage:
        endPage = totPage

    start = (currentPage-1)*pageSize

    boardList = Board.objects.all()[start:start+pageSize]
   

    context = {"boardList": boardList, "boardCount":boardCount,
               "startPage":startPage, "endPage":endPage, "totPage":totPage, "currentPage":currentPage,
               "range":range(startPage, endPage+1), "blockPage":blockPage}
    return render(request, "board/list.html", context)
