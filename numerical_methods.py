import math

def f_derivative(t, V, Qin, k):
    """
    Función f(t, V) de la EDO: dV/dt = Qin - k * V
    V: Volumen útil de la represa en Mm³ (millones de metros cúbicos)
    Qin: Caudal constante de afluentes y deshielo (Mm³/día)
    k: Coeficiente de extracción por consumo y evaporación (día⁻¹)
    """
    return Qin - (k * V)

def exact_solution(t, V0, Qin, k):
    """
    Solución analítica exacta:
    V(t) = (Qin / k) + (V0 - Qin / k) * exp(-k * t)
    """
    if k == 0:
        return V0 + Qin * t
    V_eq = Qin / k
    return V_eq + (V0 - V_eq) * math.exp(-k * t)

def heun_method(V0, Qin, k, t_max, h):
    """
    Método de Heun (Runge-Kutta de 2.° orden con predictor y corrector):
    Predictor (Euler): V_pred = V_i + h * f(t_i, V_i)
    Corrector: V_{i+1} = V_i + (h/2) * [ f(t_i, V_i) + f(t_i + h, V_pred) ]
    """
    t_values = [0.0]
    V_values = [float(V0)]
    
    steps = int(round(t_max / h))
    t = 0.0
    V = float(V0)
    
    for _ in range(steps):
        # Pendiente inicial
        f1 = f_derivative(t, V, Qin, k)
        # Predictor (Euler estándar)
        V_pred = V + h * f1
        # Pendiente final estimada
        f2 = f_derivative(t + h, V_pred, Qin, k)
        # Corrección por promedio de pendientes
        V_next = V + (h / 2.0) * (f1 + f2)
        
        t += h
        V = V_next
        t_values.append(round(t, 4))
        V_values.append(V)
        
    return t_values, V_values

def rk4_method(V0, Qin, k, t_max, h):
    """
    Método clásico de Runge-Kutta de 4.° orden (RK4):
    k1 = f(t_i, V_i)
    k2 = f(t_i + h/2, V_i + (h/2)*k1)
    k3 = f(t_i + h/2, V_i + (h/2)*k2)
    k4 = f(t_i + h, V_i + h*k3)
    V_{i+1} = V_i + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
    """
    t_values = [0.0]
    V_values = [float(V0)]
    
    steps = int(round(t_max / h))
    t = 0.0
    V = float(V0)
    
    for _ in range(steps):
        k1 = f_derivative(t, V, Qin, k)
        k2 = f_derivative(t + 0.5 * h, V + 0.5 * h * k1, Qin, k)
        k3 = f_derivative(t + 0.5 * h, V + 0.5 * h * k2, Qin, k)
        k4 = f_derivative(t + h, V + h * k3, Qin, k)
        
        V_next = V + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        
        t += h
        V = V_next
        t_values.append(round(t, 4))
        V_values.append(V)
        
    return t_values, V_values

def calculate_critical_day(V0, Qin, k, V_crit):
    """
    Calcula el día exacto en que la represa alcanza el umbral crítico de alerta roja (V_crit).
    Utiliza la solución analítica invertida:
    t_crit = - (1/k) * ln[ (V_crit - Qin/k) / (V0 - Qin/k) ]
    """
    if V0 <= V_crit:
        return 0.0
    
    if k == 0:
        return None
        
    V_eq = Qin / k
    if V_eq >= V_crit:
        # El embalse se estabiliza por encima del umbral crítico (nunca colapsa)
        return -1.0
        
    numerator = V_crit - V_eq
    denominator = V0 - V_eq
    
    ratio = numerator / denominator
    if ratio <= 0:
        return None
        
    t_crit = - (1.0 / k) * math.log(ratio)
    return round(t_crit, 2)

def run_simulation(V0, Qin, k, V_crit, t_max, h1=1.0, h2=0.5):
    """
    Ejecuta la simulación completa:
    - Analítica
    - Heun y RK4 para el paso principal h1
    - Heun y RK4 para el paso fino h2 (para cumplir el requisito de comparar dos tamaños de paso)
    - Tablas de error absoluto y relativo (%)
    """
    # 1. Simulación con paso h1
    t_h1, v_heun_h1 = heun_method(V0, Qin, k, t_max, h1)
    _, v_rk4_h1 = rk4_method(V0, Qin, k, t_max, h1)
    
    # 2. Simulación con paso h2
    t_h2, v_heun_h2 = heun_method(V0, Qin, k, t_max, h2)
    _, v_rk4_h2 = rk4_method(V0, Qin, k, t_max, h2)
    
    # 3. Construcción de tabla de comparación para h1
    table_data = []
    max_err_heun_h1 = 0.0
    max_err_rk4_h1 = 0.0
    
    v_exact_h1 = []
    for i, t in enumerate(t_h1):
        v_ex = exact_solution(t, V0, Qin, k)
        v_exact_h1.append(v_ex)
        
        # Errores Heun
        err_abs_heun = abs(v_ex - v_heun_h1[i])
        err_rel_heun = (err_abs_heun / abs(v_ex)) * 100.0 if v_ex != 0 else 0.0
        
        # Errores RK4
        err_abs_rk4 = abs(v_ex - v_rk4_h1[i])
        err_rel_rk4 = (err_abs_rk4 / abs(v_ex)) * 100.0 if v_ex != 0 else 0.0
        
        if err_rel_heun > max_err_heun_h1:
            max_err_heun_h1 = err_rel_heun
        if err_rel_rk4 > max_err_rk4_h1:
            max_err_rk4_h1 = err_rel_rk4
            
        table_data.append({
            "step": i,
            "t": t,
            "exact": round(v_ex, 5),
            "heun": round(v_heun_h1[i], 5),
            "err_abs_heun": f"{err_abs_heun:.6e}",
            "err_rel_heun": round(err_rel_heun, 5),
            "rk4": round(v_rk4_h1[i], 5),
            "err_abs_rk4": f"{err_abs_rk4:.6e}",
            "err_rel_rk4": round(err_rel_rk4, 5)
        })
        
    # 4. Cálculo de errores máximos para h2 (comparación de pasos)
    max_err_heun_h2 = 0.0
    max_err_rk4_h2 = 0.0
    for i, t in enumerate(t_h2):
        v_ex = exact_solution(t, V0, Qin, k)
        err_rel_heun_h2 = (abs(v_ex - v_heun_h2[i]) / abs(v_ex)) * 100.0 if v_ex != 0 else 0.0
        err_rel_rk4_h2 = (abs(v_ex - v_rk4_h2[i]) / abs(v_ex)) * 100.0 if v_ex != 0 else 0.0
        if err_rel_heun_h2 > max_err_heun_h2:
            max_err_heun_h2 = err_rel_heun_h2
        if err_rel_rk4_h2 > max_err_rk4_h2:
            max_err_rk4_h2 = err_rel_rk4_h2

    # 5. Día crítico
    critical_day = calculate_critical_day(V0, Qin, k, V_crit)
    
    # 6. Redacción automática de conclusión comunitaria
    if critical_day and critical_day > 0:
        interpretacion = (
            f"Bajo las condiciones de estiaje simuladas, la represa alcanzará el nivel de alerta roja "
            f"({V_crit} Mm³) en aproximadamente {critical_day:.1f} días. "
            f"El software alerta que EPSAS debe implementar racionamiento preventivo por distritos "
            f"antes del día {math.floor(critical_day - 5)} para extender la reserva hídrica."
        )
    elif critical_day == -1.0:
        interpretacion = (
            f"El volumen de la represa se estabiliza por encima del umbral crítico ({V_crit} Mm³). "
            f"El aporte de afluentes es suficiente para sostener el consumo actual sin riesgo inminente."
        )
    else:
        interpretacion = "La represa ya se encuentra en o por debajo del umbral crítico de alerta roja."
        
    comparativa_pasos = {
        "h1": {
            "valor": h1,
            "max_err_heun": max_err_heun_h1,
            "max_err_rk4": max_err_rk4_h1
        },
        "h2": {
            "valor": h2,
            "max_err_heun": max_err_heun_h2,
            "max_err_rk4": max_err_rk4_h2
        }
    }
    
    return {
        "t_h1": t_h1,
        "v_exact": [round(x, 5) for x in v_exact_h1],
        "v_heun": [round(x, 5) for x in v_heun_h1],
        "v_rk4": [round(x, 5) for x in v_rk4_h1],
        "v_crit_line": [float(V_crit)] * len(t_h1),
        "table": table_data,
        "critical_day": critical_day,
        "interpretation": interpretacion,
        "step_comparison": comparativa_pasos,
        "max_err_heun": max_err_heun_h1,
        "max_err_rk4": max_err_rk4_h1
    }
