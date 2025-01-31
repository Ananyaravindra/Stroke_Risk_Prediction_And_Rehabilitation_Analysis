FROM python:3.9-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    dos2unix \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip && \
    pip install pipenv && \
    mkdir data

# Install additional Python packages for AI features
RUN pip install streamlit tensorflow opencv-python-headless pandas numpy textblob plotly scikit-learn pillow requests nltk && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Install TFLite runtime
RUN pip install https://github.com/alexeygrigorev/tflite-aws-lambda/raw/main/tflite/tflite_runtime-2.7.0-cp39-cp39-linux_x86_64.whl

COPY ["data/model.tflite", "./data/"]

COPY [ "Pipfile", "Pipfile.lock", "*.py", "start.sh", "./" ]

# Convert line endings and set permissions
RUN dos2unix start.sh && \
    chmod +x start.sh

# Install dependencies from Pipfile
RUN pipenv install --system --deploy

# Install textblob corpora
RUN python -m textblob.download_corpora

# Expose ports
EXPOSE 8051
EXPOSE 8080


# Add healthcheck for Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["./start.sh"]