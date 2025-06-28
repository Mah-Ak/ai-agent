FROM phidata/python:3.12

ARG USER=app
ARG APP_DIR=/app
ENV APP_DIR=${APP_DIR}

# Create user and home directory
RUN groupadd -g 61000 ${USER} \
  && useradd -g 61000 -u 61000 -ms /bin/bash -d ${APP_DIR} ${USER}

WORKDIR ${APP_DIR}

# Copy requirements.txt
COPY requirements.txt ./

# Install requirements
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip sync requirements.txt --system && \
    pip install --no-cache-dir qdrant-client==1.7.3 google-generativeai==0.8.3

# Copy project files
COPY . .

# Set permissions for the /app directory
RUN chown -R ${USER}:${USER} ${APP_DIR}

# Switch to non-root user
USER ${USER}

# اضافه کردن volume برای دیتابیس
VOLUME ["/app/data"]

# تغییر مسیر دیتابیس به volume
ENV DB_PATH=/app/data/agents.db

# اضافه کردن volume برای فایل‌های استاتیک
VOLUME ["/app/storage"]

# تنظیم دسترسی‌ها
RUN mkdir -p /app/storage/charts && \
    chown -R ${USER}:${USER} /app/storage

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["chill"]
