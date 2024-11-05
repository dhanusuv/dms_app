from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

app = Flask(__name__)
CORS(app)

# Database connection
db_uri = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_uri)

@app.route('/datasets', methods=['GET'])
def get_datasets():
    allData = []
    with engine.connect() as connection:
        result = connection.execute(text("""SELECT * FROM dms_app_tenv.datasets""")).fetchall()
        for row in result:
            dataset = {
                'id': row[0],
                'dataset_name': row[1],
                'frequency': row[2],
                'source': row[3],
                'version': row[4]
            }
            allData.append(dataset)
    print("All Data:", allData)        
    return jsonify(allData)

@app.route('/datasets', methods=['POST'])
def add_dataset():
    new_dataset = request.json
    with engine.connect() as connection:
        with connection.begin() as trans:
            try:
                cursor = connection.connection.cursor()
                cursor.execute(
                    '''
                    INSERT INTO dms_app_tenv.datasets (dataset_name, frequency, source, version)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, dataset_name, frequency, source, version
                    ''',
                    (
                        new_dataset.get('dataset_name'),
                        new_dataset.get('frequency'),
                        new_dataset.get('source'),
                        new_dataset.get('version')
                    )
                )
                new_record = cursor.fetchone()
                trans.commit()
                
                # Map the new record to a dictionary
                if new_record:
                    dataset = {
                        'id': new_record[0],
                        'dataset_name': new_record[1],
                        'frequency': new_record[2],
                        'source': new_record[3],
                        'version': new_record[4]
                    }
                    print("Inserted New Record:", dataset)
                    return jsonify(dataset)
                else:
                    print("Insert failed: No record returned.")
                    return jsonify({'error': 'Failed to insert dataset'}), 500
            except Exception as e:
                trans.rollback()
                print("Error inserting dataset:", str(e))
                return jsonify({'error': str(e)}), 500
            finally:
                cursor.close()

@app.route('/datasets/<int:id>', methods=['DELETE'])
def delete_dataset(id):
    with engine.connect() as connection:
        with connection.begin() as trans:
            try:
                cursor = connection.connection.cursor()
                cursor.execute(
                    '''
                    DELETE FROM dms_app_tenv.datasets
                    WHERE id = %s
                    RETURNING id, dataset_name, frequency, source, version
                    ''',
                    (id,)
                )
                deleted_record = cursor.fetchone()
                trans.commit()
                
                # Map the deleted record to a dictionary
                if deleted_record:
                    dataset = {
                        'id': deleted_record[0],
                        'dataset_name': deleted_record[1],
                        'frequency': deleted_record[2],
                        'source': deleted_record[3],
                        'version': deleted_record[4]
                    }
                    print("Deleted Record:", dataset)
                    return jsonify(dataset)
                else:
                    print("Delete failed: Dataset not found.")
                    return jsonify({'error': 'Dataset not found'}), 404
            except Exception as e:
                trans.rollback()
                print("Error deleting dataset:", str(e))
                return jsonify({'error': str(e)}), 500
            finally:
                cursor.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
