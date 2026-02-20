# user/models.py
from django.db import models
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
# 用户注册信息表
class UserLoginInfo(models.Model):
    user_name = models.CharField(verbose_name="用户昵称", max_length=100, primary_key=True)
    user_time = models.DateTimeField(verbose_name="首次登录时间", auto_now_add=True)
    user_star = models.IntegerField(verbose_name="用户星级/积分", default=0)
    user_password=models.CharField(verbose_name="账号密码", max_length=100)

    class Meta:
        db_table = "user_login_info"
        verbose_name = "用户登录信息"
        verbose_name_plural = verbose_name

def generate_avatar_filename(instance, filename):
    # 1. 强制提取文件后缀（防止无后缀文件）
    ext = os.path.splitext(filename)[1] if os.path.splitext(filename)[1] else '.jpg'
    # 2. 生成唯一文件名（UUID）
    unique_filename = f"{uuid.uuid4()}{ext}"
    # 3. 加固：即使user_name为空/None/空字符串，也用unknown目录
    user_dir = instance.user_name.strip() if (instance.user_name and isinstance(instance.user_name, str)) else "unknown"
    # 4. 强制拼接三级路径：avatars/用户目录/唯一文件名
    final_path = os.path.join('avatars', user_dir, unique_filename)
    # 调试：打印生成的路径，确认是否正确
    print(f"【路径生成】最终存储路径：{final_path}")
    return final_path

# 个人资料表（包含 user_school 字段）
class UserProfile(models.Model):
    SEX_CHOICES = [(0, "男"), (1, "女"), (None, "未知")]
    user_name = models.CharField(verbose_name="用户昵称", max_length=100, primary_key=True)
    user_sex = models.IntegerField(verbose_name="性别", choices=SEX_CHOICES, null=True, blank=True)
    user_birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    user_school = models.CharField(verbose_name="学校名称", max_length=100, null=True, blank=True)
    avatar = models.ImageField(
        verbose_name="头像文件",
        upload_to=generate_avatar_filename,  # 自动生成存储路径
        default='avatars/default.jpg',  # 默认头像（需提前放在 media/avatars/default.jpg）
        null=True,
        blank=True
    )
    user_avatar = models.CharField(verbose_name="头像URL", max_length=255, null=True, blank=True)
    user_wx_num=  models.CharField(verbose_name="微信号", max_length=100, null=True, blank=True)
    user_phone_num = models.CharField(verbose_name="手机号", max_length=100, null=True, blank=True)
    user_introduction = models.CharField(verbose_name="个人简介", max_length=500, null=True, blank=True)
    update_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    class Meta:
        db_table = "user_profile"
        verbose_name = "个人资料"
        verbose_name_plural = verbose_name
        # 正确的索引：给自身的 user_school 字段建索引
        indexes = [
            models.Index(fields=["user_school"], name="idx_user_profile_school"),
        ]

    def save(self, *args, **kwargs):
        # 1. 定义正确的base_url（替换成你的服务器公网IP）
        base_url = "http://192.168.1.16:8000"  # 或服务器公网IP：http://47.xx.xx.xx:8000
        # 2. 获取旧头像（用于删除）
        old_instance = None
        old_avatar = None
        if self.pk:
            try:
                old_instance = UserProfile.objects.get(pk=self.pk)
                old_avatar = old_instance.avatar
            except UserProfile.DoesNotExist:
                old_avatar = None

        # ========== 核心修改：先保存数据，生成新的avatar.url ==========
        # 第一次save：保存avatar文件，生成新的url
        super().save(*args, **kwargs)

        # 3. 拼接新的绝对URL（此时avatar.url已更新为新路径）
        if self.avatar and hasattr(self.avatar, 'url'):
            # 修复Windows路径分隔符问题，强制用/
            avatar_relative_url = self.avatar.url.replace('\\', '/')
            # 拼接绝对URL
            new_avatar_url = f"{base_url}{avatar_relative_url}"
            # 仅当URL变化时才更新，避免重复保存
            if self.user_avatar != new_avatar_url:
                self.user_avatar = new_avatar_url
                # 第二次save：只更新user_avatar字段，提高效率
                super().save(update_fields=['user_avatar', 'update_time'])
                print(f"【URL更新】user_avatar已更新为：{self.user_avatar}")  # 调试日志

        # 4. 删除旧头像文件（原有逻辑）
        if old_avatar and old_avatar != self.avatar:
            default_avatar_path = 'avatars/default.jpg'
            if old_avatar.name != default_avatar_path and default_storage.exists(old_avatar.path):
                try:
                    default_storage.delete(old_avatar.path)
                    print(f"【旧文件删除】已删除：{old_avatar.path}")
                except Exception as e:
                    print(f"【删除失败】{str(e)}")