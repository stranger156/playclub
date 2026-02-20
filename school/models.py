from django.db import models

class SchoolList(models.Model):
    # 自增主键（推荐添加，方便后续关联/查询）
    id = models.BigAutoField(primary_key=True, verbose_name="自增主键")
    school_name = models.CharField(verbose_name="学校名称", max_length=100)
    city = models.CharField(verbose_name="所属城市", max_length=50)

    class Meta:
        db_table = "school_list"  # 数据库表名
        verbose_name = "学校列表"  # 后台显示的单名
        verbose_name_plural = verbose_name  # 后台显示的复数名（中文无需复数）
        # 唯一约束：避免同一城市重复录入同一学校
        unique_together = ("school_name", "city")
        # 索引：添加表名前缀，保证全局唯一
        indexes = [
            # 规范命名：idx_表名_字段名
            models.Index(fields=["city"], name="idx_school_list_city"),
            # 可选：添加学校名称索引（如果经常按学校名查询）
            models.Index(fields=["school_name"], name="idx_school_list_name"),
        ]