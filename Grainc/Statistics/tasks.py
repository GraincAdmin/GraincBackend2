from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from Statistics.models import CompanyCarryingCapacity, CompanyRetention, CompanyRevenueStatistics
from AuthUser.models import ServiceUser
from Transaction.models import Membership_Article_Donation_Record
from django.db.models import Sum
# @shared_task
# def calculate_carrying_capacity():
    
#     # daily new customer
#     current_day = timezone.now()
#     new_customers = ServiceUser.objects.filter(sign_up_date=current_day).only('sign_up_date')

#     new_customers_count = new_customers.count()


#     # MAU
#     current_year = timezone.now().year
#     current_month = timezone.now().month
#     mau_users = ServiceUser.objects.filter(last_login__year=current_year, last_login__month=current_month).only('sign_up_date')


#     carrying_capacity = 
@shared_task
def calculate_seven_day_retention():
    now = timezone.now()

    # 7일 이내에 계산된 리텐션이 있는지 확인
    try:
        latest_calculation = CompanyRetention.objects.order_by('-create_date').only('create_date')[0]
    except IndexError:
        latest_calculation = None

    if latest_calculation is None or latest_calculation.create_date <= now:
        # 현재 시간과 7일 전 날짜 계산
        seven_days_ago = now - timedelta(days=7)

        # 7일 이전에 가입한 사용자 조회
        users_signed_up_before_seven_days = ServiceUser.objects.filter(sign_up_date__lt=seven_days_ago)

        # 7일 이내에 활동한 사용자 수 계산
        active_users_within_seven_days = users_signed_up_before_seven_days.filter(last_active_date__gte=seven_days_ago).count()

        # 총 사용자 수
        total_users_count = users_signed_up_before_seven_days.count()

        # 리텐션 비율 계산
        retention_rate = 0
        if total_users_count > 0:
            retention_rate = (active_users_within_seven_days / total_users_count) * 100
            
            retention_record = CompanyRetention(
                retention=retention_rate,
                retention_period='weekly'
            )

            try:
                retention_record.save()  # 데이터베이스에 저장
            except:
                return

        # 결과 출력
        print(f"Total users signed up before 7 days: {total_users_count}")
        print(f"Active users within the last 7 days: {active_users_within_seven_days}")
        print(f"7-day retention rate: {retention_rate:.2f}%")
    
    else:
        return
    

from Grainc.Global_Variable.MembershipPrice import membership_price, donation_allowed_amount

@shared_task
def calculate_daily_revenue():

    """ 
    매출 계산 방법은 이와 같다:

    맴버십 유저 = mu
    맴버십 가격 = x + y
    멤버십 확정 매출 = x
    멤버십 후원가능 예치금 = y
    후원된 금액 = dm

    매월 1일에 확정매출이 계산된다 X 월에 새로 가입하는 유저가 있을 수도 있어서, 계산에 포함한다,
    확정매출 = x * mu

    그리고 매일 후원이 된 금액을 계산해서 예상매출을 디스카운트 한다,
    예상매출 = 확정매출 + {mu(y) - dm}

    이렇게 하면 매일 새롭게 후원이 된 금액을 반영한 예상매출이 계산 된다,
    이때 중요한 것이, 보유해야할 예치금 계산이 필요하다. 후원금 출금을 위해서,
    
    이를 위해 dm은 따로 보관한다
    """

    total_membership_users = ServiceUser.objects.filter(is_membership=True).only('is_membership').count()
    
    # important fix based on company policy
    defined_revenue = (membership_price - donation_allowed_amount) * total_membership_users

    today = timezone.now()
    month_start = today.replace(day=1) # fix

    donated_amount = Membership_Article_Donation_Record.objects.filter(donation_date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0


    projected_revenue = defined_revenue + ((donation_allowed_amount * total_membership_users) - donated_amount)

    # Prepare the JSON data for projected revenue
    json_defined_revenue = {today.strftime('%Y-%m-%d'): defined_revenue}
    json_projected_revenue = {today.strftime('%Y-%m-%d'): projected_revenue}

    json_revenue_data = {
        'create_date': today.strftime('%Y-%m-%d'), 
        'defined_revenue': defined_revenue,
        'projected_revenue': projected_revenue
    }


    # Create or update revenue data
    revenue_data = CompanyRevenueStatistics.objects.filter(
        create_date__year=today.year,
        create_date__month=today.month
    ).first()

    if revenue_data:
        if revenue_data.combined_revenue_data is None:
            revenue_data.combined_revenue_data = []
        

        existing_combined_revenue_data = next(
            (entry for entry in revenue_data.combined_revenue_data if entry.get('create_date') == today.strftime('%Y-%m-%d')), 
            None
        )
        if existing_combined_revenue_data:
            existing_combined_revenue_data['defined_revenue'] = defined_revenue
            existing_combined_revenue_data['projected_revenue'] = projected_revenue
        else:
            revenue_data.combined_revenue_data.append(json_revenue_data)
        
        revenue_data.defined_revenue = defined_revenue
        revenue_data.save()

    else:
        CompanyRevenueStatistics.objects.create(
            defined_revenue=defined_revenue, 
            combined_revenue_data = [json_revenue_data]
        )

    



    



