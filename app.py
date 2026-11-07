import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, SimulationReport
from numerical_methods import run_simulation

app = Flask(__name__)

# Configuración de Base de Datos (PostgreSQL en producción o local)
# Compatible con Render, Railway, Neon o PostgreSQL local
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Render suele entregar URLs con 'postgres://', SQLAlchemy requiere 'postgresql://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback automático a SQLite local para pruebas inmediatas si PostgreSQL local no está activo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///represas_local.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'represas-lapaz-secret-2026')

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    try:
        data = request.get_json() or {}
        V0 = float(data.get('V0', 4.5))
        Qin = float(data.get('Qin', 0.02))
        k = float(data.get('k', 0.035))
        V_crit = float(data.get('V_crit', 1.04))
        t_max = float(data.get('t_max', 60.0))
        h1 = float(data.get('h1', 1.0))
        h2 = float(data.get('h2', 0.5))
        
        # Validaciones básicas
        if V0 <= 0 or k <= 0 or t_max <= 0 or h1 <= 0 or h2 <= 0:
            return jsonify({"success": False, "error": "Los parámetros deben ser valores positivos mayores a cero."}), 400
        if h1 > t_max or h2 > t_max:
            return jsonify({"success": False, "error": "El tamaño de paso h no puede ser mayor al tiempo total."}), 400

        results = run_simulation(V0, Qin, k, V_crit, t_max, h1, h2)
        results["success"] = True
        return jsonify(results)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/save', methods=['POST'])
def api_save():
    try:
        data = request.get_json() or {}
        
        report = SimulationReport(
            title=data.get('title', 'Simulación de Represa Paceña'),
            represa_name=data.get('represa_name', 'Incachaca'),
            description=data.get('description', ''),
            initial_volume=float(data.get('V0', 4.5)),
            inflow_rate=float(data.get('Qin', 0.02)),
            depletion_rate=float(data.get('k', 0.035)),
            critical_threshold=float(data.get('V_crit', 1.04)),
            time_days=int(float(data.get('t_max', 60))),
            step_size_h1=float(data.get('h1', 1.0)),
            step_size_h2=float(data.get('h2', 0.5)),
            days_to_critical=float(data.get('critical_day', 0.0)) if data.get('critical_day') is not None else None,
            max_error_heun=float(data.get('max_err_heun', 0.0)),
            max_error_rk4=float(data.get('max_err_rk4', 0.0)),
            conclusion=data.get('interpretation', '')
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Informe guardado exitosamente en la base de datos.",
            "report_id": report.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/history')
def history():
    reports = SimulationReport.query.order_by(SimulationReport.created_at.desc()).all()
    return render_template('history.html', reports=reports)

@app.route('/api/report/<int:report_id>', methods=['GET'])
def get_report(report_id):
    report = SimulationReport.query.get_or_404(report_id)
    return jsonify({"success": True, "report": report.to_dict()})

@app.route('/api/report/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    try:
        report = SimulationReport.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        return jsonify({"success": True, "message": "Informe eliminado."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Puerto dinámico para entornos cloud como Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
