from django.db import models
from datetime import datetime

# Create your models here.
class Board(models.Model):
    writer = models.CharField(null=False, max_length=50)
    title = models.CharField(null=False, max_length=200)
    content = models.TextField(null=False)
    hit = models.IntegerField(default=0)
    post_date = models.DateField(default=datetime.now, blank=True)
    filename = models.CharField(null=True, blank=True, default='', max_length=500)
    filesize = models.IntegerField(default=0)
    down = models.IntegerField(default=0)

def hit_up(self):
    self.hit += 1
    
def down_up(self):
    self.down += 1

class Comment(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)  # 부모를 지우면 자식도 같이 지워짐, 외래키설정 할 때 객체를 넣어줘야함.
    writer = models.CharField(null=False, max_length=50)
    content = models.TextField(null=False)
    post_date = models.DateTimeField(default=datetime.now, blank=True)