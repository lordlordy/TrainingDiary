from django.db import models


class RestingHeartRate(models.Model):
    date = models.DateField(unique=True)
    value = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f'{self.date.strftime("%Y-%m-%d")} HR: {self.value}'

    def data_dictionary(self):
        return {'iso8601DateString': self.date.isoformat(),
                'value': float(self.value)}


class RMSSD(models.Model):
    date = models.DateField(unique=True)
    value = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f'{self.date.strftime("%Y-%m-%d")} rMSSD: {self.value}'

    def data_dictionary(self):
        return {'iso8601DateString': self.date.isoformat(),
                'value': float(self.value)}


class SDNN(models.Model):
    date = models.DateField(unique=True)
    value = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f'{self.date.strftime("%Y-%m-%d")} SDNN: {self.value}'

    def data_dictionary(self):
        return {'iso8601DateString': self.date.isoformat(),
                'value': float(self.value)}


class KG(models.Model):
    date = models.DateField(unique=True)
    value = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f'{self.date.strftime("%Y-%m-%d")} KG: {self.value}'

    def data_dictionary(self):
        return {'iso8601DateString': self.date.isoformat(),
                'value': float(self.value)}


class FatPercentage(models.Model):
    date = models.DateField(unique=True)
    value = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f'{self.date.strftime("%Y-%m-%d")} Fat%: {self.value}'

    def data_dictionary(self):
        return {'iso8601DateString': self.date.isoformat(),
                'value': float(self.value)}
