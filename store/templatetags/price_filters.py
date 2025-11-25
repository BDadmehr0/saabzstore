from django import template

register = template.Library()


@register.filter
def toman(value):
    if value is None:
        return ""
    try:
        # تبدیل Decimal/float به int
        value = int(float(value))

        # فرمت هزارگان
        formatted = f"{value:,}".replace(",", "٬")

        # تبدیل ارقام انگلیسی به فارسی
        persian_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
        return formatted.translate(persian_digits)
    except:
        return value
