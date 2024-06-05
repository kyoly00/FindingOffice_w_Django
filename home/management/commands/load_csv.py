import csv
from home.models import ShareOffice
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Load a csv file into the ShareOffice database'

    def handle(self, *args, **kwargs):
        csv_file_path = "SharedOffice_data.csv"

        # 'Y' 또는 'N'을 1 또는 0으로 변환하는 함수
        def y_n_to_int(value):
            if value == 'Y':
                return 1
            elif value == 'N':
                return 0
            else:
                return None

        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # 헤더 스킵
            for row in reader:
                ShareOffice.objects.create(
                    so_name=row[0],
                    so_address=row[1],
                    so_latitude=float(row[2]),
                    so_longitude=float(row[3]),
                    so_postal_code=row[4],
                    so_price=float(row[5]),
                    so_max_people=int(row[6]),
                    so_mon_open=row[7],
                    so_mon_close=row[8],
                    so_tues_open=row[9],
                    so_tues_close=row[10],
                    so_wed_open=row[11],
                    so_wed_close=row[12],
                    so_thur_open=row[13],
                    so_thur_close=row[14],
                    so_fri_open=row[15],
                    so_fri_close=row[16],
                    so_sat_open=row[17],
                    so_sat_close=row[18],
                    so_sun_open=row[19],
                    so_sun_close=row[20],
                    so_ac=y_n_to_int(row[21]),
                    so_cafe=y_n_to_int(row[22]),
                    so_printer=y_n_to_int(row[23]),
                    so_parcel_sndng_posbl=y_n_to_int(row[24]),
                    so_doorlock=y_n_to_int(row[25]),
                    so_elect_outlet=y_n_to_int(row[26]),
                    so_fax=y_n_to_int(row[27]),
                    so_n24h_oper=y_n_to_int(row[28]),
                    so_n365d_oper=y_n_to_int(row[29]),
                    so_heater=y_n_to_int(row[30]),
                    so_parkng_posbl=y_n_to_int(row[31]),
                    so_cmnuse_lounge=y_n_to_int(row[32]),
                    so_cmnuse_kitchen=y_n_to_int(row[33]),
                    so_wpu=y_n_to_int(row[34]),
                    so_rooftop=y_n_to_int(row[35]),
                    so_refreshments_provd=y_n_to_int(row[36]),
                    so_indivdl_locker=y_n_to_int(row[37]),
                    so_tv=y_n_to_int(row[38]),
                    so_wboard=y_n_to_int(row[39]),
                    so_wifi=y_n_to_int(row[40]),
                    so_bath_fclty=y_n_to_int(row[41])

                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded the csv into database'))
