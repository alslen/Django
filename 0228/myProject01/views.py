from django.shortcuts import render, redirect
from django.http.response import JsonResponse, HttpResponse
from urllib import response
import urllib.parse 
from myapp01.models import Board, Comment
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import math

# Create your views here.
UPLOAD_DIR = 'D:/DJANGOWORK/upload/'  # 파일을 업로드할 경로

# write_form
def write_form(request):  
    return render(request, 'board/write.html')   # write.html로 넘어가라

# insert
@csrf_exempt  # csrf를 사용하지 x
def insert(request):  # request를 통해서 board객체를 생성해줘야함.
    fname = ''
    fsize = 0

    if 'file' in request.FILES:  # 파일이 여러개 있다면
        file = request.FILES['file']  
        fname = file.name  
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR,fname), 'wb')  # 파일을 읽어옴(UPLOAD_DIR위치의 fname이라는 이름으로 파일을 씀.)
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        
    dto = Board(writer = request.POST['writer'],    
                title = request.POST['title'],
                content = request.POST['content'],
                filename = fname,
                filesize = fsize
                )
    dto.save()  # DB에 값 저장
    return redirect('/list')  # list로 페이지 이동

# 전제보기
def list(request):
    # request로 form태그로 넘어오는 값을 받아올 수 있음.
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')  # word라는 이름의 값이 없으면 공백으로 값을 저장
    field = request.GET.get('field', 'title') # field값이 있으면 값을 받아오고 없으면 title로 저장

   
    # count
    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word)|Q(title__contains=word)|Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
        # content에 word가 포함되어져 있는 데이터를 뽑아서 저장
        boardCount = Board.objects.filter(Q(content__contains=word)).count()  # and, or, not등을 묶어주기 위해 사용하기 위해 Q연산자 사용
    else:
       boardCount = Board.objects.all().count()

    #page
    pageSize = 5
    blockPage = 3  # 이전과 다음 사이의 페이지 개수
    currentPage = int(page)  
    ### 123 [다음]      [이전]456[다음]  [이전] 7 (89)
    totPage = math.ceil(boardCount/pageSize) # 전체 페이지 수  # ex>7
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1
    endPage = startPage+blockPage-1 # 9 (현재 페이지가 7이라면)

    if endPage > totPage:  # endPage가 전체 페이지 수보다 크다면
        endPage = totPage
    
    start = (currentPage-1)*pageSize
 
    # 내용
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word)|Q(title__contains=word)|Q(content__contains=word)).order_by('-idx')[start:start+pageSize] # start에서 start+pageSize까지 게시물을 슬라이싱해라.
    elif field == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(Q(title__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field == 'content':
        # content에 word가 포함되어져 있는 데이터를 뽑아서 저장
        boardList = Board.objects.filter(Q(content__contains=word)).order_by('-idx')[start:start+pageSize]  # and, or, not등을 묶어주기 위해 사용하기 위해 Q연산자 사용
    else:
        boardList = Board.objects.all().order_by('-idx')[start:start+pageSize] # select sql문이 만들어짐. / all은 Board테이블의 모든 것을 가져옴.

    context = {'boardList': boardList, 'boardCount': boardCount, 'field':field, 'word':word,
               'startPage':startPage, 'blockPage':blockPage, 'totPage':totPage, 'endPage':endPage, 
               'range':range(startPage, endPage+1), 'currentPage':currentPage}   # dictionary형태로 값을 전달 해줘야함.
    return render(request, 'board/list.html',context)

# 상세보기  # detail_idx/?idx=1방식으로 전달
def detail_idx(request):  # request가 idx를 가지고 있음. 
    id = request.GET['idx']
    # print('id : ', id)
    dto = Board.objects.get(idx=id) # idx가 id인 튜플 하나를 가져옴.
    dto.hit_up()  # 조회수 1증가 수행
    dto.save()  # 조회수가 1증가하기 때문에 테이블에 반영하기 위해 save해줘야함.
    ################## comment list
    # board_idx가 id인 값들을 찾아서 내림차순으로 정렬한 값을 commentList에 담음.
    commentList = Comment.objects.filter(board_idx=id).order_by('-idx')  # 내림차순으로 정렬
    return render(request, 'board/detail.html', {'dto':dto, 'commentList':commentList})

# 상세보기 detail/1/ ==>  detail/<int:board_idx>
def detail(request, board_idx):
    print('board_idx : ', board_idx)
    dto = Board.objects.get(idx=board_idx)
    dto.hit_up()
    dto.save()
    ######## comment list
    commentList = Comment.objects.filter(board_idx=board_idx).order_by('idx')  # filter() : query set(ResultSet)이 반환됨.
    # print(commentList.query)
    return render(request, 'board/detail.html', {'dto':dto, 'commentList':commentList})

# update_form
def update_form(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    return render(request, 'board/update.html', {'dto':dto})

# update
@csrf_exempt  #post방식이기 때문에 csrf사용 안한다고 선언
def update(request):

    id = request.POST['idx']  # id값은 반드시 있어야 함.
    # dto = Board.objects.get(idx=id)
    # fname = dto.filename
    # fsize = dto.filesize

    if 'file' in request.FILES: # 파일을 선택했을 때
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chuck in file.chunks():
            fp.write(chuck)
        fp.close()
    else: # 파일이 선택되지 않았다면
       dto = Board.objects.get(idx=id)
       fname = dto.filename
       fsize = dto.filesize
       
    dto_update = Board(id, writer = request.POST['writer'],
                        title = request.POST['title'],
                        content = request.POST['content'],
                        filename = fname, filesize = fsize)
    dto_update.save()

    return redirect('/list/')

# delete
def delete(request, board_idx):

    Board.objects.get(idx=board_idx).delete() 
    return redirect("/list/")

# 다운로드 수 1증가
def download_count(request):
    id = request.GET['idx']
    print('id : ', id)
    dto = Board.objects.get(idx=id)
    dto.down_up()  # 다운로드 수 증가
    dto.save()
    count = dto.down  # count는 json형태로 전달해야함. -> JsonResponse를 import를 시킴
    print('count : ', count)
    return JsonResponse({'idx':id, 'count':count})  # Json형태로 값 반환

# 다운로드
def download(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    path = UPLOAD_DIR+dto.filename  
    filename = urllib.parse.quote(dto.filename)  # urllib을 통해서 경로를 유추해옴.
    print('filename : ', filename)
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')  # 어플리케이션의 stream형태로 읽어옴.
        response['Content-Disposition'] = "attachment; filename*=UTF-8''{0}".format(filename)
    return response

###### comment

# comment insert
@csrf_exempt
def comment_insert(request):
    id = request.POST['idx']  # hidden값으로 idx를 받아오기 때문에
    cdto = Comment(board_idx = id, writer= 'aaa', # 외래키 설정하지 않고 강제적으로 idx값을 주입했음.
                   content=request.POST['content'])
    cdto.save()
    # return redirect("/detail_idx?idx="+id)
    return redirect("/detail/"+id)
