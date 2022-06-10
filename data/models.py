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


class Month(models.Model):
    name = models.CharField('Название месяца', max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.name} '

    class Meta:
        verbose_name = 'Месяца'
        verbose_name_plural = 'Месяцы'


class ItemAccount(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=False, null=True, related_name='accounts', verbose_name='ИП')
    account = models.CharField('Номер счета', max_length=255, blank=True, null=True)
    limit = models.DecimalField('Лимит в месяц', decimal_places=2, max_digits=10, default=0)
    income_amount = models.DecimalField('Сумма прихода', decimal_places=2, max_digits=10, default=0)
    outcome_amount = models.DecimalField('Сумма расхода', decimal_places=2, max_digits=10, default=0)
    withdraw_amount = models.DecimalField('Сумма выводов', decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f'Для ИП {self.item.name} #{self.account}'

    class Meta:
        verbose_name = 'Расчетный счет'
        verbose_name_plural = 'Расчетные счета'


class ItemRow(models.Model):
    account = models.ForeignKey( ItemAccount, on_delete=models.CASCADE, blank=False, null=True, related_name='rows', verbose_name='Р/С')
    month = models.ForeignKey( Month, on_delete=models.CASCADE, blank=False, null=True, verbose_name='Месяц')
    amount = models.DecimalField('Сумма', decimal_places=2, max_digits=10, blank=True, null=True)
    is_income = models.BooleanField('Это приход', default=False)
    is_outcome = models.BooleanField('Это расход', default=False)
    is_withdraw = models.BooleanField('Это вывод', default=False)
    description = RichTextUploadingField('Описание', blank=True, null=True)
    created = models.DateField('Дата', blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     month = RowMonthAmount.objects.filter(item=self,month=self.month)
    #     if not month:
    #         month = RowMonthAmount.objects.create()
    #         month.item = self
    #         month.month = self.month
    #         month.save()
    #
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f'Для Р/С {self.account.account}'

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'


def row_post_save(sender, instance, created, **kwargs):

    month_row_amont,is_created = RowMonthAmount.objects.get_or_create(item_id=instance.account.id, month_id=instance.month.id)
    if is_created:
        print('is_created')
    if created:
        # month_row_amont = RowMonthAmount.objects.get(item=instance,month=instance.month)
        # month_row_amont = RowMonthAmount.objects.filter(item=instance, month=instance.month)
        print('month_row_amont', month_row_amont)
        # if not month_row_amont:
        #     month_row_amont = RowMonthAmount.objects.create(item=instance, month=instance.month)

        if instance.is_income:
            instance.account.income_amount += instance.amount
            instance.account.item.income_amount += instance.amount
            month_row_amont.income_amount += instance.amount

        if instance.is_outcome:
            instance.account.outcome_amount += instance.amount
            instance.account.item.outcome_amount += instance.amount
            month_row_amont.outcome_amount += instance.amount

        if instance.is_withdraw:
            instance.account.withdraw_amount += instance.amount
            instance.account.item.withdraw_amount += instance.amount
            month_row_amont.withdraw_amount += instance.amount
        instance.account.save()
        instance.account.item.save()
        month_row_amont.save()

post_save.connect(row_post_save, sender=ItemRow)

def row_pre_delete(sender, instance, using, **kwargs):
    month_row_amont = RowMonthAmount.objects.get(item_id=instance.account.id,
                                                                       month_id=instance.month.id)
    if instance.is_income:
        instance.account.income_amount -= instance.amount
        instance.account.item.income_amount -= instance.amount
        month_row_amont.income_amount -= instance.amount

    if instance.is_outcome:
        instance.account.outcome_amount -= instance.amount
        instance.account.item.outcome_amount -= instance.amount
        month_row_amont.outcome_amount -= instance.amount

    if instance.is_withdraw:
        instance.account.withdraw_amount -= instance.amount
        instance.account.item.withdraw_amount -= instance.amount
        month_row_amont.withdraw_amount -= instance.amount
    instance.account.save()
    instance.account.item.save()
    month_row_amont.save()

pre_delete.connect(row_pre_delete, sender=ItemRow)


class RowMonthAmount(models.Model):
    item = models.ForeignKey(ItemAccount, on_delete=models.CASCADE, blank=False, null=True, related_name='month_amount')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, blank=False, null=True)
    income_amount = models.DecimalField('Сумма прихода', decimal_places=2, max_digits=10, default=0)
    outcome_amount = models.DecimalField('Сумма расхода', decimal_places=2, max_digits=10, default=0)
    withdraw_amount = models.DecimalField('Сумма выводов', decimal_places=2, max_digits=10, default=0)




class ItemFile(models.Model):
    item = models.ForeignKey(ItemRow, on_delete=models.CASCADE, blank=False, null=True, related_name='files')
    name = models.CharField('Название файла', max_length=255, blank=True, null=True)
    file = models.FileField('Файл', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

