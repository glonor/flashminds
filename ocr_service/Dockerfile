FROM clearlinux/tesseract-ocr

EXPOSE 5003

# Copy the trained data for English language to the container
COPY eng.traineddata /usr/share/tessdata

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD python -u ocr_api.py