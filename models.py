from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SimulationReport(db.Model):
    """
    Modelo de Base de Datos (PostgreSQL) para almacenar las simulaciones
    y variables del ejercicio de modelado de represas en La Paz.
    """
    __tablename__ = 'simulation_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, default="Simulación de Represa")
    represa_name = db.Column(db.String(100), nullable=False, default="Incachaca")
    description = db.Column(db.Text, nullable=True)
    
    # Variables y parámetros del modelo matemático (EDO)
    initial_volume = db.Column(db.Float, nullable=False)      # V0 en Mm³
    inflow_rate = db.Column(db.Float, nullable=False)         # Qin en Mm³/día
    depletion_rate = db.Column(db.Float, nullable=False)      # k en día⁻¹
    critical_threshold = db.Column(db.Float, nullable=False)  # V_crit en Mm³
    time_days = db.Column(db.Integer, nullable=False)         # t_max en días
    step_size_h1 = db.Column(db.Float, nullable=False)        # h1 (ej: 1.0)
    step_size_h2 = db.Column(db.Float, nullable=False)        # h2 (ej: 0.5)
    
    # Resultados calculados
    days_to_critical = db.Column(db.Float, nullable=True)     # Días al colapso/alerta roja
    max_error_heun = db.Column(db.Float, nullable=True)       # Error relativo máx Heun %
    max_error_rk4 = db.Column(db.Float, nullable=True)        # Error relativo máx RK4 %
    conclusion = db.Column(db.Text, nullable=True)            # Interpretación comunitaria
    
    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "represa_name": self.represa_name,
            "description": self.description,
            "initial_volume": self.initial_volume,
            "inflow_rate": self.inflow_rate,
            "depletion_rate": self.depletion_rate,
            "critical_threshold": self.critical_threshold,
            "time_days": self.time_days,
            "step_size_h1": self.step_size_h1,
            "step_size_h2": self.step_size_h2,
            "days_to_critical": self.days_to_critical,
            "max_error_heun": self.max_error_heun,
            "max_error_rk4": self.max_error_rk4,
            "conclusion": self.conclusion,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
