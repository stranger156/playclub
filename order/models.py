from django.db import models
from datetime import date
# 3. 招募信息表
class RecruitOrder(models.Model):
    STATUS_CHOICES = [(0, "招募中"), (1, "招募结束"), (2, "已取消")]
    order_id = models.CharField(
        verbose_name="订单ID",
        max_length=64,
        primary_key=True,
        editable=False  # 禁止在后台编辑，避免手动修改
    )
    user_name = models.CharField(verbose_name="发起人昵称", max_length=50)
    order_introduction = models.CharField(verbose_name="招募介绍", max_length=1000)
    max_num = models.IntegerField(verbose_name="招募最大人数")
    current_num = models.IntegerField(verbose_name="当前人数", default=1)
    order_time = models.DateField(verbose_name="招募时间",max_length=50)
    order_date = models.DateField(verbose_name="发布时间",default=date.today)
    status = models.IntegerField(verbose_name="订单状态", choices=STATUS_CHOICES, default=0)
    star = models.IntegerField(verbose_name="热度", default=0)

    class Meta:
        db_table = "recruit_order"
        verbose_name = "招募信息"
        verbose_name_plural = verbose_name
        indexes = [
            # 修正：加表名前缀 recruit_order
            models.Index(fields=["user_name"], name="idx_recruit_order_user_name"),
            models.Index(fields=["order_time"], name="idx_recruit_order_time"),
            models.Index(fields=["status"], name="idx_recruit_order_status")
        ]

# 4. 招募用户表
class RecruitUser(models.Model):
    STATUS_CHOICES = [(0, "参与"), (1, "已退出")]
    order_id = models.CharField(verbose_name="订单ID", max_length=64)
    user_name = models.CharField(verbose_name="参与人昵称", max_length=100)
    is_owner = models.IntegerField(verbose_name="是否发起人", default=0)  # 0-否，1-是
    join_time = models.DateTimeField(verbose_name="加入时间", auto_now_add=True)
    status = models.IntegerField(verbose_name="订单状态", choices=STATUS_CHOICES, default=0)

    class Meta:
        db_table = "recruit_user"
        verbose_name = "招募用户"
        verbose_name_plural = verbose_name
        unique_together = ("order_id", "user_name")  # 唯一约束
        indexes = [
            # 修正：加表名前缀 recruit_user
            models.Index(fields=["order_id"], name="idx_recruit_user_order_id"),
            models.Index(fields=["user_name"], name="idx_recruit_user_user_name")  # 唯一名称
        ]

