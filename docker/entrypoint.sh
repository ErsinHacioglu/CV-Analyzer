#!/bin/sh
set -e

until python -c "
import os
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL', ''), pool_pre_ping=True)
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
" 2>/dev/null; do
  sleep 2
done

python -c "from cv_analyzer.db import init_database; init_database()"

if [ ! -f cv_analyzer/ml/saved_models/resume_classifier.joblib ]; then
  python cv_analyzer/ml/train_classifier.py
fi

exec streamlit run main.py --server.address 0.0.0.0 --server.port 8501
