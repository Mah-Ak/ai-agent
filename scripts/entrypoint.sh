#!/bin/bash

############################################################################
# Container Entrypoint script
############################################################################

if [[ "$PRINT_ENV_ON_LOAD" = true || "$PRINT_ENV_ON_LOAD" = True ]]; then
  echo "=================================================="
  printenv
  echo "=================================================="
fi

############################################################################
# Wait for Services
############################################################################

if [[ "$WAIT_FOR_DB" = true || "$WAIT_FOR_DB" = True ]]; then
  dockerize \
    -wait tcp://$DB_HOST:$DB_PORT \
    -timeout 300s
fi

if [[ "$WAIT_FOR_REDIS" = true || "$WAIT_FOR_REDIS" = True ]]; then
  dockerize \
    -wait tcp://$REDIS_HOST:$REDIS_PORT \
    -timeout 300s
fi

############################################################################
# Install requirements
############################################################################

if [[ "$INSTALL_REQUIREMENTS" = true || "$INSTALL_REQUIREMENTS" = True ]]; then
  echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  echo "Installing requirements: $REQUIREMENTS_FILE_PATH"
  pip3 install -r $REQUIREMENTS_FILE_PATH
  echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
fi

############################################################################
# Start App
############################################################################

# نصب پکیج‌های مورد نیاز
pip install --no-cache-dir qdrant-client==1.7.3 numpy>=1.22.0

# اضافه کردن مسیر پروژه به PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/app"

case "$1" in
  chill)
    echo "Starting Streamlit App..."
    cd /app && streamlit run app/Home.py --server.port=8501 --server.address=0.0.0.0
    ;;
  *)
    echo "در حال اجرا: $@"
    exec "$@"
    ;;
esac

