from django.db import models
class Customer(models.Model):
    cus_email = models.EmailField(primary_key=True)
    cus_password = models.CharField(max_length=255)
    cus_name = models.CharField(max_length=20)
    cus_gender = models.CharField(max_length=20)
    cus_company = models.CharField(max_length=20)
    cus_phone = models.IntegerField()
    cus_address = models.CharField(max_length=20)
    cus_latitude = models.FloatField(default = 0.0)
    cus_longitude = models.FloatField(default = 0.0)

class ShareOffice(models.Model):
    so_name = models.CharField(max_length=100)
    so_address = models.CharField(max_length=200)
    so_latitude = models.FloatField()
    so_longitude = models.FloatField()
    so_postal_code = models.CharField(max_length=20)
    so_price = models.FloatField()
    so_max_people = models.IntegerField()
    so_mon_open = models.CharField(max_length=10)
    so_mon_close = models.CharField(max_length=10)
    so_tues_open = models.CharField(max_length=10)
    so_tues_close = models.CharField(max_length=10)
    so_wed_open = models.CharField(max_length=10)
    so_wed_close = models.CharField(max_length=10)
    so_thur_open = models.CharField(max_length=10)
    so_thur_close = models.CharField(max_length=10)
    so_fri_open = models.CharField(max_length=10)
    so_fri_close = models.CharField(max_length=10)
    so_sat_open = models.CharField(max_length=10)
    so_sat_close = models.CharField(max_length=10)
    so_sun_open = models.CharField(max_length=10)
    so_sun_close = models.CharField(max_length=10)
    so_ac = models.BooleanField()
    so_cafe = models.BooleanField()
    so_printer = models.BooleanField()
    so_parcel_sndng_posbl = models.BooleanField()
    so_doorlock = models.BooleanField()
    so_elect_outlet = models.BooleanField()
    so_fax = models.BooleanField()
    so_n24h_oper = models.BooleanField()
    so_n365d_oper = models.BooleanField()
    so_heater = models.BooleanField()
    so_parkng_posbl = models.BooleanField()
    so_cmnuse_lounge = models.BooleanField()
    so_cmnuse_kitchen = models.BooleanField()
    so_wpu = models.BooleanField()
    so_rooftop = models.BooleanField()
    so_refreshments_provd = models.BooleanField()
    so_indivdl_locker = models.BooleanField()
    so_tv = models.BooleanField()
    so_wboard = models.BooleanField()
    so_wifi = models.BooleanField()
    so_bath_fclty = models.BooleanField()

    def facilities(self):
        facilities_list = []
        if self.so_ac: facilities_list.append('AC')
        if self.so_cafe: facilities_list.append('CAFE')
        if self.so_printer: facilities_list.append('PRINTER')
        if self.so_parcel_sndng_posbl: facilities_list.append('PARCEL SENDING')
        if self.so_doorlock: facilities_list.append('DOORLOCK')
        if self.so_elect_outlet: facilities_list.append('ELECT OUTLET')
        if self.so_fax: facilities_list.append('FAX')
        if self.so_n24h_oper: facilities_list.append('24H OPER')
        if self.so_n365d_oper: facilities_list.append('365D OPER')
        if self.so_heater: facilities_list.append('HEATER')
        if self.so_parkng_posbl: facilities_list.append('PARKING')
        if self.so_cmnuse_lounge: facilities_list.append('LOUNGE')
        if self.so_cmnuse_kitchen: facilities_list.append('KITCHEN')
        if self.so_wpu: facilities_list.append('WPU')
        if self.so_rooftop: facilities_list.append('ROOFTOP')
        if self.so_refreshments_provd: facilities_list.append('REFRESHMENTS')
        if self.so_indivdl_locker: facilities_list.append('LOCKER')
        if self.so_tv: facilities_list.append('TV')
        if self.so_wboard: facilities_list.append('WHITEBOARD')
        if self.so_wifi: facilities_list.append('WIFI')
        if self.so_bath_fclty: facilities_list.append('BATH FACILITY')
        return facilities_list

class Reservation(models.Model):
    cus_email = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='cus_email', default='default_email@example.com')
    so_id = models.ForeignKey(ShareOffice, on_delete=models.CASCADE)
    re_people_num = models.IntegerField(default=0)
    re_start_time = models.DateTimeField()
    re_end_time = models.DateTimeField()
    re_cancel = models.BooleanField(default=False)
    re_cancel_date = models.DateTimeField(null=True, blank=True, default=None)

class Location(models.Model):
    cus_email = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='cus_email', default='default_email@example.com')
    lo_latitude = models.FloatField(max_length=30)
    lo_longitude = models.FloatField(max_length=30)

