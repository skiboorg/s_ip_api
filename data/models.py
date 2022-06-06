from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.signals import post_save, pre_delete

class Item(models.Model):
    name = models.CharField('Название ИП', max_length=255, blank=True, null=True)
    status = models.CharField('Статус', max_length=255, blank=True, null=True)
    description = RichTextUploadingField('Инфа', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    income_amount = models.DecimalField('Сумма прихода', decimal_places=2, max_digits=10, default=0)
    outcome_amount = models.DecimalField('Сумма расхода', decimal_places=2, max_digits=10, default=0)
    withdraw_amount = models.DecimalField('Сумма выводов', decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'ИП'
        verbose_name_plural = 'ИП'



class ItemRow(models.Model):
    item = models.ForeignKey( Item, on_delete=models.CASCADE, blank=False, null=True, related_name='rows', verbose_name='ИП')
    amount = models.DecimalField('Сумма', decimal_places=2, max_digits=10, blank=True, null=True)
    is_income = models.BooleanField('Это приход', default=False)
    is_outcome = models.BooleanField('Это расход', default=False)
    is_withdraw = models.BooleanField('Это вывод', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Для ИП {self.item.name}'

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'


def row_post_save(sender, instance, created, **kwargs):

    if created:
        if instance.is_income:
            instance.item.income_amount += instance.amount

        if instance.is_outcome:
            instance.item.outcome_amount += instance.amount

        if instance.is_withdraw:
            instance.item.withdraw_amount += instance.amount
        instance.item.save()

post_save.connect(row_post_save, sender=ItemRow)

def row_pre_delete(sender, instance, using, **kwargs):

    if instance.is_income:
        instance.item.income_amount -= instance.amount

    if instance.is_outcome:
        instance.item.outcome_amount -= instance.amount

    if instance.is_withdraw:
        instance.item.withdraw_amount -= instance.amount
    instance.item.save()

pre_delete.connect(row_pre_delete, sender=ItemRow)

class ItemFile(models.Model):
    item = models.ForeignKey(ItemRow, on_delete=models.CASCADE, blank=False, null=True, related_name='files')
    name = models.CharField('Название файла', max_length=255, blank=True, null=True)
    file = models.FileField('Файл', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

