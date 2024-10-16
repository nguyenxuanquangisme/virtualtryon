from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, handle_file
import shutil
import boto3
import time
import io
import secrets
import string

def generate_private_key(length=25):
    # Xác định các ký tự có thể xuất hiện trong khóa
    characters = string.ascii_letters + string.digits
    # Tạo khóa ngẫu nhiên với độ dài đã cho
    private_key = ''.join(secrets.choice(characters) for _ in range(length))
    return private_key



s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIAZQ3DTG4U7QOPUJPC',
    aws_secret_access_key='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',
    region_name='us-east-1'
)
bucket_name = 'fptvton'

app = Flask(__name__)

# Dữ liệu mẫu cho sản phẩm
# Dữ liệu mẫu cho sản phẩm
products = [
    {
        'id': 1,
        'name': 'DC | DBZ Vegeta T-Shirt - White',
        'price': '450.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt-1.jpg',
        'description': 'Mô tả chi tiết về T-shirt 1.'
    },
    {
        'id': 2,
        'name': 'DC | DBZ Frieza T-Shirt - Black',
        'price': '450.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt-2.jpg',
        'description': 'Mô tả chi tiết về T-shirt 2.'
    },
    {
        'id': 3,
        'name': 'Nothing Changes T-Shirt - Yellow',
        'price': '320.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt12.png',
        'description': 'Mô tả chi tiết về T-shirt 3.'
    },
    {
        'id': 4,
        'name': 'More Money More Problems',
        'price': '390.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt13.png',
        'description': 'Mô tả chi tiết về T-shirt 4.'
    },
    {
        'id': 5,
        'name': 'Jersey DC x GAM Worlds 2024 ',
        'price': '200.000',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt16.png',
        'description': 'Mô tả chi tiết về T-shirt 5.'
    },
    {
        'id': 6,
        'name': 'Thương Bạn Gái T-shirt',
        'price': '390.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt14.png',
        'description': 'Mô tả chi tiết về T-shirt 6.'
    },
    {
        'id': 7,
        'name': 'If I Play I Play To Win T-Shirt ',
        'price': '320.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt15.png',
        'description': 'Mô tả chi tiết về T-shirt 7.'
    },
    {
        'id': 8,
        'name': 'DirtyCoins Wavy Logo T-Shirt',
        'price': '390.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/t-shirt17.png',
        'description': 'Mô tả chi tiết về T-shirt 8.'
    },
]


@app.route('/')
def index():
    return render_template('index.html', products=products)



@app.route('/product/<int:product_id>',methods=['GET', 'POST'])
def product_detail(product_id):
    product = next((item for item in products if item['id'] == product_id), None)
    print(product)
    if request.method == 'POST':
        # Get the files from the form
        model_image = request.files['model_image']
        cloth_image = request.files['cloth_image']
        model_image_url = request.form.get('model_image_url')
        cloth_image_url = request.form.get('cloth_image_url')


        def process_images(model_img_path, cloth_img_path):
            # Load model and perform segmentation + virtual try-on
            # Return paths to segmentation image and try-on result

            client = Client("basso4/fptvton1")
            result = client.predict(
                human_img={"background": handle_file(model_img_path), "layers": [],
                           "composite": None},
                garm_img=handle_file(cloth_img_path),
                api_name="/tryon"
            )




            result_img, result1_img, segmentation_img = result
            return result_img,result1_img, segmentation_img

        if model_image and cloth_image_url:
            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(model_image, bucket_name, f'static/uploads/{key2}/image_model.png')
            model_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_model.png'
            # Here you would call your model processing function to generate the output
            result_img, result1_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(result1_img, bucket_name, f'static/result/{key1}/img_result1.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'
            result_img1_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result1.png'

            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url, result_img1_url=result_img1_url )


        if model_image_url and cloth_image:
            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(cloth_image, bucket_name, f'static/uploads/{key2}/image_cloth.png')
            cloth_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_cloth.png'
            # Here you would call your model processing function to generate the output
            result_img, result1_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(result1_img, bucket_name, f'static/result/{key1}/img_result1.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'
            result_img1_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result1.png'

            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url, result_img1_url=result_img1_url)




        if model_image_url and cloth_image_url:
            result_img, result1_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(result1_img, bucket_name, f'static/result/{key1}/img_result1.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'
            result_img1_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result1.png'

            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url, result_img1_url=result_img1_url)

        if model_image and cloth_image:

            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(model_image, bucket_name, f'static/uploads/{key2}/image_model.png')
            s3_client.upload_fileobj(cloth_image, bucket_name, f'static/uploads/{key2}/image_cloth.png')
            model_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_model.png'
            cloth_image_url =f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_cloth.png'

            result_img, result1_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(result1_img, bucket_name, f'static/result/{key1}/img_result1.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'
            result_img1_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result1.png'

            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url, result_img1_url=result_img1_url)

    return render_template('product_detail.html', product=product)



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True,port= 5007)
