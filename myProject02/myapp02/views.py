from django.shortcuts import render, redirect
from myapp02.models import Board, Comment
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import math
import urllib.parse
from django.db.models import Q
from django.core.paginator import Paginator

from .form import UserForm  # form.py에서 UserForm을 import


# Create your views here.
UPLOAD_DIR ='D:\\DJANGOWORK\\upload\\'

###################################
# 회원가입
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            print('signup POST is_valid')
            form.save()
        else:
            print('signup POST un_valid')

    else :
        form = UserForm()  # UserForm 객체 생성
    return render(request, "common/signup.html", {'form':form})

#######################################

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

# list_page
def list_page(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')

    boardCount = Board.objects.filter(Q(writer__contains=word)|Q(title__contains=word)|Q(content__contains=word)).count()
    boardList = Board.objects.filter(Q(writer__contains=word)|Q(title__contains=word)|Q(content__contains=word)).order_by('-id')

    pageSize = 5
    # 페이징 처리(Paginator 사용)
    paginator = Paginator(boardList, pageSize)  # Paginator객체 생성
    page_obj = paginator.get_page(page)  # 한페이지에 대한 정보를 가져옴.
    # print('page_obj : ', page_obj)  # page_obj :  <Page 1 of 4>
    
    context = {'page_list':page_obj, 'word':word, 'boardCount':boardCount, 'boardList':boardList}
    return render(request, "board/list_page.html", context)

# list
def list(request):
 
    page = request.GET.get('page', 1)
    field = request.GET.get('field', 'title')
    word = request.GET.get('word', '')

    # count
    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word)|Q(title__contains=word)|Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()
    elif field == 'title':
         boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
         boardCount = Board.objects.filter(Q(content__contains=word)).count()
    else :
        boardCount = Board.objects.all().count()
        
    pageSize = 5
    blockPage = 3
    currentPage = int(page)
    start = (currentPage-1)*pageSize
    ## 123[다음]  [이전]456[다음]  [이전]789[다음]
    totPage = math.ceil(boardCount/pageSize)  # 전체 페이지 ex>7
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1 
    endPage = startPage+blockPage-1

    if endPage > totPage:
        endPage = totPage

    # content
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word)|Q(title__contains=word)|Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'title':
         boardList = Board.objects.filter(Q(title__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'content':
         boardList = Board.objects.filter(Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    else :
        boardList = Board.objects.all().order_by('-id')[start:start+pageSize]
   
    context = {"boardList": boardList, "boardCount":boardCount,
               "startPage":startPage, "endPage":endPage, "totPage":totPage, "currentPage":currentPage,
               "range":range(startPage, endPage+1), "blockPage":blockPage, "field":field, "word":word}
    return render(request, "board/list.html", context)


# download_count
def download_count(request):
    id = request.GET['id']  # GET으로 넘어오는 id값을 request로 받아올 수 있음.
    print('id : ', id)
    board = Board.objects.get(id=id)
    board.down_up()  # 다운로드 수 1 증가
    board.save()  # 증가된 다운로드 수 DB에 저장
    count = board.down # 다운로드 수
    print('count : ', count)
    return JsonResponse({'id':id, 'count':count})  # json객체로 값을 넘겨줘야하기 때문에 JsonResponse를 사용 / JsonResponse는 키와 value의 형태로 값을 전달해야함.

# download
def download(request):
    id = request.GET['id']
    board = Board.objects.get(id=id)
    path = UPLOAD_DIR+board.filename  
    filename = urllib.parse.quote(board.filename)   # 파일명을 파싱
    with open(path, 'rb') as file:  # path에 있는 파일을 읽어와서 -> 다운로드를 시킴.
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = "attachment; filename*=UTF-8''{0}".format(filename)

    return response

# detail
def detail(request, board_id):
    board = Board.objects.get(id=board_id)
    # 조회수 증가
    board.hit_up()
    board.save()

    return render(request, 'board/detail.html', {'board': board})

# 삭제
def delete(request, board_id):
    Board.objects.get(id=board_id).delete()
    return redirect("/list")

# 수정폼
def update_form(request, board_id):
    print('지금 여기')
    board = Board.objects.get(id=board_id)
    print(board)
    return render(request,"board/update.html",{'board':board})

# 수정
@csrf_exempt
def update(request):
    id = request.POST['id']
    board = Board.objects.get(id=id)

    # 파일을 수정하지 않을 때 
    fname = board.filename   # 파일을 수정하지 않을때는 있는 그대로의 값을 저장하기 위해 
    fsize = board.filesize

    if 'file' in request.FILES : # file 수정
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR,fname),'wb')  # 파일을 폴더 안에 업로드 시켜오기 위해 
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()   

    update_board = Board(id, writer = request.POST['writer'], title = request.POST['title'],
                         content = request.POST['content'], filename = fname, filesize = fsize)
    update_board.save()

    return redirect("/list")

# comment_insert
@csrf_exempt
def comment_insert(request):
    id = request.POST['id']
    writer = request.POST['writer']

    comment = Comment(writer=writer, content=request.POST['content'], board_id=id)
    comment.save()

    return redirect("/detail/"+id)

