from django.shortcuts import render, redirect
from django.http.response import JsonResponse, HttpResponse
from urllib import response
import urllib.parse 
from myapp01.models import Board, Comment
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
UPLOAD_DIR = 'D:/DJANGOWORK/upload/'  # 파일을 업로드할 경로

# write_form
def write_form(request):  
    return render(request, 'board/write.html')   # write.html로 넘어가라

# insert
@csrf_exempt  # csrf를 사용하지 x
def insert(request):  # request를 통해서 board객체를 생성해줘야함.
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
    else :
          dto = Board(writer = request.POST['writer'],    
                    title = request.POST['title'],
                    content = request.POST['content']
                    )

    dto.save()  # DB에 값 저장
    return redirect('/list')  # list로 페이지 이동

def list(request):
    boardList = Board.objects.all() # select sql문이 만들어짐. / all은 Board테이블의 모든 것을 가져옴.
    # print(boardList.query) # query : sql 출력문을 보여줌.
    boardCount = Board.objects.all().count()
    print(boardCount) # sql 출력문이 보임.
    context = {'boardList': boardList, 'boardCount': boardCount}
    # dictionary형태로 값을 전달 해줘야함.
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
    ######## comment
    commentList = Comment.objects.filter(board_idx=board_idx).order_by('idx')
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
