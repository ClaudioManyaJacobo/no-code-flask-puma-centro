from babel.dates import format_date
from datetime import datetime

mes_actual = format_date(datetime.now(), "MMMM", locale="es").upper()
print(mes_actual)  # Ejemplo: "ENERO"
