from django.db import models

class ContainerNotification(models.Model):
    crn_container_no = models.CharField(
        max_length=30, primary_key=True, db_column='CRN_CONTAINER_NO'
    )
    crn_status = models.IntegerField(default=0, db_column='CRN_STATUS')

    class Meta:
        db_table = 'CNT_RECVD_NOTIFICATION'
        managed  = False

    def __str__(self):
        return self.crn_container_no



class ChartOfAccounts(models.Model):
    TYPE_CHOICES = [
        ('asset', 'Asset'), ('liability', 'Liability'),
        ('equity', 'Equity'), ('revenue', 'Revenue'), ('expense', 'Expense'),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Chart of Account'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Journal(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('posted', 'Posted'), ('cancelled', 'Cancelled')]

    reference = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.date}"


class JournalEntry(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.account} Dr:{self.debit} Cr:{self.credit}"


class Invoice(models.Model):
    TYPE_CHOICES = [('sales', 'Sales Invoice'), ('purchase', 'Purchase Invoice')]
    STATUS_CHOICES = [('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'), ('cancelled', 'Cancelled')]

    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    party_name = models.CharField(max_length=200)
    party_email = models.EmailField(blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.party_name}"

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount


class Expense(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    submitted_by = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"
