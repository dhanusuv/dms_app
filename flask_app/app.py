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
    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM dms_app.datasets'))
        datasets = [dict(row) for row in result]
    return jsonify(datasets)

@app.route('/datasets', methods=['POST'])
def add_dataset():
    new_dataset = request.json
    with engine.connect() as connection:
        with connection.begin() as trans:
            try:
                cursor = connection.connection.cursor()
                cursor.execute(
                    '''
                    INSERT INTO dms_app.datasets (dataset_name, frequency, source, version)
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
                if new_record:
                    return jsonify(dict(new_record))
                else:
                    return jsonify({'error': 'Failed to insert dataset'}), 500
            except Exception as e:
                trans.rollback()
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
                    DELETE FROM dms_app.datasets
                    WHERE id = %s
                    RETURNING id, dataset_name, frequency, source, version
                    ''',
                    (id,)
                )
                deleted_record = cursor.fetchone()
                trans.commit()
                if deleted_record:
                    return jsonify(dict(deleted_record))
                else:
                    return jsonify({'error': 'Dataset not found'}), 404
            except Exception as e:
                trans.rollback()
                return jsonify({'error': str(e)}), 500
            finally:
                cursor.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
