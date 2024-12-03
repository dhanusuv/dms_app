from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

app = Flask(__name__)
CORS(app)

# Database connection
db_uri = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_uri)

# Get all datasets
@app.route('/datasets', methods=['GET'])
def get_datasets():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM dms_app_tenv.datasets")).fetchall()
            datasets = [
                {
                    'id': row[0],
                    'dataset_name': row[1],
                    'frequency': row[2],
                    'source': row[3],
                    'version': row[4]
                }
                for row in result
            ]
        print("Fetched datasets:", datasets)
        return jsonify(datasets)
    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return jsonify({'error': str(e)}), 500

# Add a new dataset
@app.route('/datasets', methods=['POST'])
def add_dataset():
    new_dataset = request.json
    try:
        with engine.connect() as connection:
            with connection.begin() as trans:
                result = connection.execute(
                    text("""
                        INSERT INTO dms_app_tenv.datasets (dataset_name, frequency, source, version)
                        VALUES (:dataset_name, :frequency, :source, :version)
                        RETURNING id, dataset_name, frequency, source, version
                    """),
                    {
                        'dataset_name': new_dataset.get('dataset_name'),
                        'frequency': new_dataset.get('frequency'),
                        'source': new_dataset.get('source'),
                        'version': new_dataset.get('version')
                    }
                )
                new_record = result.fetchone()
                if new_record:
                    dataset = dict(zip(result.keys(), new_record))
                    print("Inserted dataset:", dataset)
                    return jsonify(dataset)
                else:
                    raise Exception("Insert operation failed")
    except Exception as e:
        print(f"Insert error: {e}")
        return jsonify({'error': str(e)}), 500

# Fetch paginated data from the rvu.source_rvu table
@app.route('/source_rvu', methods=['GET'])
def get_source_rvu():
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        offset = (page - 1) * per_page

        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT 
                        hcpcs, "MOD", description, "STATUS CODE", "NOT USED FOR MEDICARE PAYMENT", 
                        "WORK RVU", "NON-FAC PE RVU", "NON-FAC NA INDICATOR", 
                        "FACILITY PE RVU", "FACILITY NA INDICATOR", "MP RVU", 
                        "NON-FACILITY TOTAL", "FACILITY TOTAL", "PCTC IND", 
                        "GLOB DAYS", "PRE OP", "INTRA OP", "POST OP", "MULT PROC", 
                        "BILAT SURG", "ASST SURG", "CO-SURG", "TEAM SURG", "ENDO BASE", 
                        "CONV FACTOR", "PHYSICIAN SUPERVISION OF DIAGNOSTIC PROCEDURES", 
                        "CALCULATION FLAG", "DIAGNOSTIC IMAGING FAMILY INDICATOR", 
                        "NON-FACILITY PE USED FOR OPPS PAYMENT AMOUNT", 
                        "FACILITY PE USED FOR OPPS PAYMENT AMOUNT", 
                        "MP USED FOR OPPS PAYMENT AMOUNT"
                    FROM rvu.source_rvu
                    LIMIT :per_page OFFSET :offset
                """),
                {'per_page': per_page, 'offset': offset}
            )
            rows = result.fetchall()

            total_count = connection.execute(
                text("SELECT COUNT(*) FROM rvu.source_rvu")
            ).scalar()

            column_names = result.keys()
            data = [dict(zip(column_names, row)) for row in rows]

            return jsonify({
                'data': data,
                'total_count': total_count,
                'page': page,
                'per_page': per_page
            })
    except Exception as e:
        print(f"Error fetching source_rvu: {e}")
        return jsonify({'error': str(e)}), 500

# Fetch data dynamically based on dataset ID
@app.route('/dataset_table/<int:dataset_id>', methods=['GET'])
def get_table_by_dataset(dataset_id):
    try:
        with engine.connect() as connection:
            mapping_result = connection.execute(
                text("""
                    SELECT dataset_name
                    FROM dms_app_tenv.datasets
                    WHERE id = :dataset_id
                """),
                {'dataset_id': dataset_id}
            ).fetchone()

            if not mapping_result:
                return jsonify({'error': f'No dataset mapping found for ID {dataset_id}'}), 404

            schema_name = 'rvu'
            table_name = mapping_result[0].replace(' ', '_').lower()

            query = text(f"SELECT * FROM {schema_name}.{table_name} LIMIT 100")
            result = connection.execute(query).fetchall()

            column_names = result.keys()
            data = [dict(zip(column_names, row)) for row in result]

            return jsonify({
                'data': data,
                'columns': column_names
            })
    except Exception as e:
        print(f"Error fetching table for dataset ID {dataset_id}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
