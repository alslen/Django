from django.db import models
from datetime import datetime

# Create your models here.
class Board(models.Model):
    idx = models.AutoField(primary_key=True)  # 자동 증가/기본키
    writer = models.CharField(null=False, max_length=50)
    title = models.CharField(null=False, max_length=200)
    content = models.TextField(null=False)
    hit = models.IntegerField(default=0) # 기본값을 주기 위해 default를 사용
    post_date = models.DateTimeField(default=datetime.now, blank=True) # 작성시간의 기본값을 현재시간, 빈값 들어갈 수 있게 만들었음.
    filename = models.CharField(null=True, blank=True, default='', max_length=500)
    filesize = models.IntegerField(default=0)
    down = models.IntegerField(default=0)   # 다운로드 횟수 

    def hit_up(self):
        self.hit += 1  # 조회수 증가하는 함수
    
    def down_up(self): # 다운로드 횟수 증가하는 함수
        self.down += 1

# 댓글 DB
class Comment(models.Model):
    idx = models.AutoField(primary_key=True)
    board_idx = models.IntegerField(null=False)
    writer = models.CharField(null=False, max_length=50)
    content = models.TextField(null=False)
    post_date = models.DateTimeField(default=datetime.now, blank=True)


